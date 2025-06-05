defmodule Paxos do
  require Logger
  use GenServer

  defstruct name: nil, participants: [], upper: nil,
            proposed_value: nil, ballot_number: 0,
            promises: %{}, accepted: %{}, decided_value: nil, processed_ballots: %{},
            status: :pending, retries: 0, leader: nil, majority_reached: false, majority_reached_shown: false

  def start(name, participants, upper) do
    {:ok, pid} = GenServer.start_link(__MODULE__, {name, participants, upper}, name: name)
    :global.register_name(name, pid)
    pid
  end

  @doc """
  Propose a value via the Paxos process.
  """
  def propose(pid, value) do
    GenServer.cast(pid, {:propose, value})
  end

  @doc """
  Start a ballot as the leader.
  """
  def start_ballot(pid) do
    GenServer.cast(pid, :start_ballot)
  end

  @doc """
  Elect a leader from the participants.
  """
  def elect_leader(pid) do
    GenServer.cast(pid, :elect_leader)
  end

  @doc """
  Get the current status of the Paxos process.
  """
  def get_status(pid) do
    GenServer.call(pid, :get_status)
  end

  @doc """
  Get the decided value of the Paxos process.
  """
  def get_val(pid) do
    GenServer.call(pid, :get_val)
  end

  @impl true
  def init({name, participants, upper}) do
    state = %__MODULE__{
      name: name,
      participants: participants,
      upper: upper,
      leader: hd(participants)  # Default to the first participant as leader initially
    }
    {:ok, state}
  end

  @impl true
  def handle_cast({:propose, value}, state) do
    if state.name == state.leader do
      Logger.info("#{state.name} (Leader) is proposing value: #{inspect(value)}")

    else
      Logger.info("#{state.name} is proprosing value: #{inspect(value)}.")
    end
    new_state = %{state | proposed_value: value, ballot_number: state.ballot_number + 1}
    start_ballot(self())
    {:noreply, new_state}
  end

  @impl true
  def handle_cast(:start_ballot, state) do
    if state.majority_reached == false do

      new_ballot = state.ballot_number + 1
      Enum.each(state.participants, fn participant ->
        case :global.whereis_name(participant) do
          pid when is_pid(pid) -> send(pid, {:prepare, new_ballot, state.name})
          :undefined -> Logger.warn("Participant #{participant} is unavailable.")
        end
      end)
      {:noreply, %{state | ballot_number: new_ballot, promises: %{}}}
    else
      if state.majority_reached_shown == false do
        Logger.info("Majority already reached")
        {:noreply, %{state | majority_reached_shown: true}}
      else
        {:noreply, state}
      end
    end
  end

  @impl true
  def handle_call(:get_status, _from, state) do
    {:reply, state.status, state}
  end

  @impl true
  def handle_call(:get_val, _from, state) do
    {:reply, state.decided_value, state}
  end

  @impl true
  def handle_info({:prepare, ballot, leader}, state) do
    if ballot > state.ballot_number do
      if Map.has_key?(state.processed_ballots, ballot) do
        {:noreply, state}
      else
        updated_state = %{state | ballot_number: ballot, processed_ballots: Map.put(state.processed_ballots, ballot, true)}
        send(:global.whereis_name(leader), {:promise, ballot, state.accepted, self()})
        {:noreply, updated_state}
      end
    else
      {:noreply, state}
    end
  end

  @impl true
  def handle_info({:promise, ballot, accepted, sender}, state) do
    if ballot == state.ballot_number and is_nil(state.decided_value) do
      updated_promises = Map.put(state.promises, sender, accepted)
      if map_size(updated_promises) >= div(length(state.participants), 2) + 1 do
        Enum.each(state.participants, fn participant ->
          case :global.whereis_name(participant) do
            pid when is_pid(pid) -> send(pid, {:accept, state.ballot_number, state.proposed_value})
          end
        end)
        {:noreply, %{state | promises: updated_promises, status: :pending}}
      else
        {:noreply, %{state | promises: updated_promises}}
      end
    else
      {:noreply, state}
    end
  end

  @impl true
  def handle_info({:accept, ballot, value}, state) do
    if ballot == state.ballot_number and is_nil(state.decided_value) do
      updated_accepted = Map.put(state.accepted, state.name, value)

      # Broadcast the updated accepted map
      Enum.each(state.participants, fn participant ->
        case :global.whereis_name(participant) do
          pid when is_pid(pid) -> send(pid, {:broadcast_accept, updated_accepted, value})
        end
      end)

      if map_size(updated_accepted) >= div(length(state.participants), 2) + 1 do
        Enum.each(state.participants, fn participant ->
          case :global.whereis_name(participant) do
            pid when is_pid(pid) -> send(pid, {:decided, value})
          end
        end)
        {:noreply, %{state | decided_value: value, status: :decided}}
      else
        {:noreply, %{state | accepted: updated_accepted}}
      end
    else
      {:noreply, state}
    end
  end

  @impl true
  def handle_info({:broadcast_accept, incoming_accepted, value}, state) do
    merged_accepted = Map.merge(state.accepted, incoming_accepted, fn _k, v1, v2 -> max(v1, v2) end)

    if map_size(merged_accepted) >= div(length(state.participants), 2) + 1 and is_nil(state.decided_value) do
      decided_value = value
      Enum.each(state.participants, fn participant ->
        case :global.whereis_name(participant) do
          pid when is_pid(pid) -> send(pid, {:decided, decided_value})
        end
      end)
      {:noreply, %{state | decided_value: decided_value, accepted: merged_accepted, status: :decided, majority_reached: true}}
    else
      {:noreply, %{state | accepted: merged_accepted}}
    end
  end

  @impl true
  def handle_info({:decided, value}, state) do
    send(state.upper, {:status, :decided, value})
    {:noreply, %{state | decided_value: value, status: :decided}}
  end

  @impl true
  def handle_info({:retry_decision, upper, value}, state) do
    if state.retries < 3 do
      send(upper, {:decided, value})
      Process.send_after(self(), {:retry_decision, upper, value}, 1000)
      {:noreply, %{state | retries: state.retries + 1}}
    else
      {:noreply, state}
    end
  end

  # Unused
  @impl true
  def handle_info({:EXIT, _pid, _reason}, state) do
    Logger.warn("A process has crahsed")
    if state.name == state.leader do
      Logger.info("Leader #{state.name} has failed. Electing a new leader.")
      send(self(), :elect_leader)
    end
    {:noreply, state}
  end

  # Unused
  @impl true
  def handle_info(:elect_leader, state) do
    new_leader = Enum.find(state.participants, fn p -> :global.whereis_name(p) != :undefined end)
    if new_leader do
      Logger.info("Electing new leader: #{new_leader}")
      new_state = %{state | leader: new_leader, ballot_number: state.ballot_number + 1}
      {:noreply, new_state}
    else
      Logger.error("No eligible participants found for leader election.")
      {:noreply, state}
    end
  end
end
