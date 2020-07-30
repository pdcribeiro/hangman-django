Vue.component('Game', {
  setup() {
    const { gameState, tryLetter } = useAPI();

    return { gameState, tryLetter };
  },

  mounted: function () {
    window.addEventListener('keyup', this.handleKeyUp);
  },

  beforeDestroy: function () {
    window.removeEventListener('keyup', this.handleKeyUp);
  },

  methods: {
    handleKeyUp: function (event) {
      const { gameState, tryLetter } = this;
      if (
        event.keyCode >= 65 &&
        event.keyCode <= 90 &&
        (!gameState.chances || gameState.winner === undefined)
      ) {
        tryLetter(event.key.toUpperCase());
      }
    },
  },

  template: `
    <Fragment v-if="gameState.chances">
      <Drawing :chancesLeft="gameState.chances" />
      <Word v-bind="gameState" />
      <WrongLetters v-bind="gameState" />
      <GameOver
        v-if="gameState.winner !== undefined"
        :winner="gameState.winner"
      />
    </Fragment>
  `,
});

Vue.component('Drawing', {
  props: {
    chancesLeft: Number,
  },

  template: `
    <div class="drawing">
      <h3>{{ chancesLeft }} chances left!</h3>
    </div>
  `,
});

Vue.component('Word', {
  props: {
    word: Array,
    letters: Array,
  },

  template: `
    <div class="word">
      <Letter
        v-for="(letter, index) in word"
        :letter="letters.includes(letter) ? letter : '\u00A0'"
        :key="index"
      />
    </div>
  `,
});

Vue.component('Letter', {
  props: {
    letter: String,
    wrong: Boolean,
  },

  template: `
    <span
      class="letter"
      :style="wrong && {
        textDecoration: 'line-through',
        color: '#940000',
      }"
    >{{ letter }}</span>
  `,
});

Vue.component('WrongLetters', {
  props: {
    word: Array,
    letters: Array,
  },

  computed: {
    wrongLetters: function () {
      return this.letters.filter(letter => !this.word.includes(letter));
    }
  },

  template: `
    <div class="wrong-letters">
      <Letter
        v-for="letter in wrongLetters"
        :letter="letter" :wrong="true" :key="letter"
      />
    </div>
  `,
});

Vue.component('GameOver', {
  props: {
    winner: String,
  },

  template: `
    <div class="gameover">
      <span v-if="winner">
        <span class="winner">'{{ winner }}' </span>
        is the winner!
      </span>
      <span v-else>Better luck next time!</span>
    </div>
  `,
});

new Vue({
  el: '#game',
});
