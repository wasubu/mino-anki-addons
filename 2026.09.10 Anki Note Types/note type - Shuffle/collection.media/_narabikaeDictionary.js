/**
 * _narabikaeDictionary.js - Anki Card Dictionary & Search Overlay Module
 * Caches word lookup results in localStorage for offline access.
 */
(function () {
  var isSearchActive = false;
  var CACHE_PREFIX = 'narabikae_dict_cache_';

  // Toggle Search Mode state
  window.toggleSearchMode = function () {
    isSearchActive = !isSearchActive;
    var btn = document.getElementById('btn-search');
    var targetBox = document.getElementById('target-box');
    var sourceBox = document.getElementById('source-box');

    if (btn) {
      if (isSearchActive) {
        btn.classList.add('active');
        btn.innerHTML = '🔍 Cancel Search';
      } else {
        btn.classList.remove('active');
        btn.innerHTML = '🔍 Search';
      }
    }

    if (targetBox) targetBox.classList.toggle('search-mode-active', isSearchActive);
    if (sourceBox) sourceBox.classList.toggle('search-mode-active', isSearchActive);
  };

  // Attach event listener on word chip clicks during search mode
  document.addEventListener('click', function (e) {
    var chip = e.target.closest('.word-chip');
    if (chip && isSearchActive) {
      e.preventDefault();
      e.stopPropagation();

      // Extract text without punctuation
      var cleanWord = chip.innerText.trim().replace(/[^\w\s'-]/g, '');
      if (cleanWord) {
        openDictionaryModal(cleanWord);
      }
      toggleSearchMode(); // Turn off search mode after selection
    }
  }, true);

  // Open overlay and load dictionary data
  window.openDictionaryModal = function (word) {
    var overlay = document.getElementById('dict-overlay');
    var body = document.getElementById('dict-modal-body');
    if (!overlay || !body) return;

    overlay.style.display = 'flex';
    body.innerHTML = '<div class="dict-loading">Loading translation for "<b>' + escapeHtml(word) + '</b>"...</div>';

    // 1. Check offline cache first
    var cachedData = getCachedWord(word);
    if (cachedData) {
      renderModalContent(word, cachedData, true);
      return;
    }

    // 2. Fetch from online API if not cached
    fetchDictionaryData(word)
      .then(function (data) {
        saveWordToCache(word, data);
        renderModalContent(word, data, false);
      })
      .catch(function (err) {
        body.innerHTML = '<div class="dict-error">Unable to load translation offline. Connect to the internet to search new words.</div>';
      });
  };

  // Close overlay modal
  window.closeDictionaryModal = function () {
    var overlay = document.getElementById('dict-overlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
  };

  // Cache utilities using localStorage
  function getCachedWord(word) {
    try {
      var item = localStorage.getItem(CACHE_PREFIX + word.toLowerCase());
      return item ? JSON.parse(item) : null;
    } catch (e) {
      return null;
    }
  }

  function saveWordToCache(word, data) {
    try {
      localStorage.setItem(CACHE_PREFIX + word.toLowerCase(), JSON.stringify(data));
    } catch (e) {}
  }

  // Fetch dictionary data using public CORS proxy & Jisho API
  function fetchDictionaryData(word) {
    var apiUrl = 'https://corsproxy.io/?' + encodeURIComponent('https://jisho.org/api/v1/search/words?keyword=' + word);

    return fetch(apiUrl)
      .then(function (res) {
        if (!res.ok) throw new Error('Network error');
        return res.json();
      })
      .then(function (json) {
        if (!json.data || json.data.length === 0) {
          throw new Error('No definitions found');
        }

        var entry = json.data[0];
        var primaryKanji = (entry.japanese[0] && entry.japanese[0].word) || entry.slug;
        var reading = (entry.japanese[0] && entry.japanese[0].reading) || '';

        // Examples formatting
        var examples = [];
        if (entry.senses && entry.senses.length > 0) {
          entry.senses.slice(0, 3).forEach(function (sense) {
            var englishDefs = sense.english_definitions.join(', ');
            examples.push({
              jp: primaryKanji + (reading ? ' (' + reading + ')' : ''),
              en: englishDefs
            });
          });
        }

        return {
          kanji: primaryKanji,
          reading: reading,
          examples: examples
        };
      });
  }

  // Render HTML inside Modal Window
  function renderModalContent(word, data, isFromCache) {
    var body = document.getElementById('dict-modal-body');
    if (!body) return;

    var headerText = word.charAt(0).toUpperCase() + word.slice(1);
    var jpHeader = data.kanji;
    if (data.reading && data.reading !== data.kanji) {
      jpHeader += ' • ' + data.reading;
    }

    var html = '<div class="dict-header">';
    html += '<h2>' + escapeHtml(headerText) + ' <span class="dict-jp-main">(' + escapeHtml(jpHeader) + ')</span></h2>';
    if (isFromCache) {
      html += '<span class="dict-cache-badge">⚡ Offline Cache</span>';
    }
    html += '</div>';

    html += '<div class="dict-examples">';
    if (data.examples && data.examples.length > 0) {
      data.examples.forEach(function (ex) {
        html += '<div class="dict-example-item">';
        html += '<div class="dict-ex-jp">' + highlightWord(ex.jp) + '</div>';
        html += '<div class="dict-ex-en">' + highlightWord(ex.en) + '</div>';
        html += '</div>';
      });
    } else {
      html += '<div class="dict-example-item">No example sentences available.</div>';
    }
    html += '</div>';

    body.innerHTML = html;
  }

  function highlightWord(text) {
    if (!text) return '';
    return escapeHtml(text).replace(/(<b>|<\/b>)/g, function (m) {
      return m;
    });
  }

  function escapeHtml(str) {
    return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
})();