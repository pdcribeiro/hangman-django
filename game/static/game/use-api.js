const { onMounted, onUnmounted, reactive } = VueCompositionAPI;

function useAPI() {
  const state = reactive({
    socket: null,
    game: null,
  });

  onMounted(() => {
    const socket = io();
    // const socket = io(`ws://${window.location.host}/game`);
    state.socket = socket;

    socket.on('connect_error', error => {
      console.error('Failed to connect WebSocket :(', error);
    });

    socket.on('connect', () => socket.emit('fetch game state'));

    socket.on('game state', newGameState => {
      if (newGameState.winner !== undefined) {
        state.game.winner = newGameState.winner;
        setTimeout(() => {
          state.game = { ...newGameState, winner: undefined };
        }, 3000);
      } else {
        state.game = newGameState;
      }
    });

    socket.on('error', error => {
      console.error('WebSocket error :(', error);
    });
  });

  onUnmounted(() => {
    state.socket.close();
  });

  function tryLetter(letter) {
    state.socket.emit('try letter', letter);
  }

  return { gameState: state.game, tryLetter };
}
