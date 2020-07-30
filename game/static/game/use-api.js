const { onMounted, onUnmounted, reactive, ref } = VueCompositionAPI;

function useAPI() {
  const webSocket = ref(null);
  const gameState = reactive({
    chances: null,
    word: null,
    letters: null,
    winner: undefined,
  });

  onMounted(() => {
    const uri = `ws://${window.location.host}/ws/game/`;
    const socket = new ReconnectingWebSocket(uri);
    webSocket.value = socket;

    socket.onmessage = event => {
      const newState = JSON.parse(event.data);
      if (validateGameState(newState)) {
        newState.word = newState.word.split('');
        newState.letters = newState.letters.split('');
        if (newState.winner !== undefined) {
          gameState.winner = newState.winner;
          setTimeout(() => {
            Object.assign(gameState, newState, { winner: undefined });
          }, 3000);
        } else {
          Object.assign(gameState, newState);
        }
      }
    };

    socket.onerror = error => console.error('WebSocket error.', error);
  });

  onUnmounted(() => {
    webSocket.value.close();
  });

  function tryLetter(letter) {
    webSocket.value.send(JSON.stringify({ letter }));
  }

  return { gameState, tryLetter };
}

function validateGameState(state) {
  return (
    typeof state.chances == 'number' &&
    typeof state.word == 'string' &&
    typeof state.letters == 'string'
  );
}
