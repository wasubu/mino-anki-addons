(() => {
  let feedbackTimeout = null;

  // Preload feedback sounds
  const feedbackSounds = {
    good: new Audio('_good.mp3'),
    again: new Audio('_again.mp3'),
    easy: new Audio('_easy.mp3'),
    hard: new Audio('_hard.mp3')
  };

  for (const key in feedbackSounds) {
    feedbackSounds[key].load();
  }

  function visualFeedbackDiv () {
    const div = document.createElement('div');
    div.classList.add('visualFeedback');
    document.body.appendChild(div);
    return div;
  }

  function onLoad () {
    for (const pos of ['top', 'bottom', 'left', 'right']) {
      const div = visualFeedbackDiv();
      div.classList.add(pos);
    }
  }

  window.avfAnswer = (ease) => {
    console.log('Ease value:', ease);

    // Play corresponding sound if it exists
    try {
      if (feedbackSounds[ease]) {
        feedbackSounds[ease].currentTime = 0;
        feedbackSounds[ease].play();
      }
    } catch (e) {
      console.error('Sound playback error:', e);
    }

    // Skip animation for "again"
    if (ease === 'again') {
      console.log('Skipping animation for "again"');
      return;
    }

    const elems = document.getElementsByClassName('visualFeedback');
    if (feedbackTimeout) {
      clearTimeout(feedbackTimeout);
    }
    for (const elem of elems) {
      elem.classList.add(ease);
    }

    feedbackTimeout = setTimeout((c) => {
      for (const elem of elems) {
        elem.classList.remove(c);
      }
    }, 300, ease);
  };

  document.readyState === 'complete'
    ? onLoad()
    : window.addEventListener('load', onLoad);
})();
