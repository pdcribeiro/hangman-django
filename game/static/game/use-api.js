const { onMounted, onUnmounted, reactive } = VueCompositionAPI;

function useAPI() {
  const state = reactive({
    socket: null,
    game: null,
  });

  onMounted(() => {
    const socket = new ReconnectingWebSocket(`ws://${window.location.host}/`);
    state.socket = socket;

    socket.onopen = () =>
      socket.send(JSON.stringify({ action: 'fetch game state' }));

    socket.onmessage = event => {
      const { action, payload: newGameState } = JSON.parse(event.data);
      if (action === 'provide game state') {
        if (newGameState.winner === undefined) {
          state.game.winner = newGameState.winner;
          setTimeout(() => {
            state.game = { ...newGameState, winner: undefined };
          }, 3000);
        } else {
          state.game = newGameState;
        }
      }
    };

    socket.onerror = error => console.error('WebSocket error.', error);
  });

  onUnmounted(() => {
    state.socket.close();
  });

  function tryLetter(letter) {
    state.socket.send(
      JSON.stringify({ action: 'try letter', payload: letter })
    );
  }

  return { gameState: state.game, tryLetter };
}
