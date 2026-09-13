// _narabikaeDictionary.js - do not modify nor delete this line - v0
/**
 * _narabikaeDictionary.js
 * Dictionary Lookup & Offline Caching Module for Anki Sentence Ordering Cards
 */

(function() {
  'use strict';

  var searchModeActive = false;
  var CACHE_PREFIX = 'narabikae_dict_cache_';

  // Built-in offline fallback dictionary for common words
  var LOCAL_DICTIONARY = {
    "worry": {
      word: "Worry",
      japanese: "心配",
      reading: "しんぱい",
      examples: [
        { jp: "僕は<span class=\"dict-highlight\">心配</span>してた", en: "I was <span class=\"dict-highlight\">worried</span>." },
        { jp: "<span class=\"dict-highlight\">心配</span>ない", en: "no <span class=\"dict-highlight\">worries</span>!" }
      ]
    },
    "worried": {
      word: "Worried",
      japanese: "心配",
      reading: "しんぱい",
      examples: [
        { jp: "僕は<span class=\"dict-highlight\">心配</span>してた", en: "I was <span class=\"dict-highlight\">worried</span>." },
        { jp: "彼女はとても<span class=\"dict-highlight\">心配</span>している。", en: "She is very <span class=\"dict-highlight\">worried</span>." }
      ]
    }
  };

  /**
   * Check if Search mode is currently active
   */
  function isSearchModeActive() {
    return searchModeActive;
  }

  /**
   * Toggle Search Mode on/off
   */
  function toggleSearchMode() {
    searchModeActive = !searchModeActive;
    var btn = document.getElementById('btn-search');
    if (btn) {
      if (searchModeActive) {
        btn.classList.add('search-mode-active');
      } else {
        btn.classList.remove('search-mode-active');
      }
    }
    return searchModeActive;
  }

  function cleanWord(w) {
    return (w || '').trim().toLowerCase().replace(/[^\w]/g, '');
  }

  /**
   * Read cached lookup from localStorage (for offline/instant use)
   */
  function getCachedResult(word) {
    var key = CACHE_PREFIX + cleanWord(word);
    try {
      var cached = localStorage.getItem(key);
      if (cached) {
        return JSON.parse(cached);
      }
    } catch (e) {
      console.warn("LocalStorage read error:", e);
    }
    return null;
  }

  /**
   * Save fetched lookup to localStorage (caching for collection.media / offline storage)
   */
  function saveCachedResult(word, data) {
    var key = CACHE_PREFIX + cleanWord(word);
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
      console.warn("LocalStorage write error:", e);
    }
  }

  /**
   * Fetch dictionary definition and sentence translation
   */
  async function fetchOnlineDefinition(rawWord) {
    var word = cleanWord(rawWord);
    if (!word) return null;

    // 1. Check local cache (Offline First)
    var cached = getCachedResult(word);
    if (cached) return cached;

    // 2. Check local fallback entries
    if (LOCAL_DICTIONARY[word]) {
      var localData = LOCAL_DICTIONARY[word];
      saveCachedResult(word, localData);
      return localData;
    }

    // 3. Fetch from API when online (Jisho API via CORS proxy)
    try {
      var targetUrl = 'https://jisho.org/api/v1/search/words?keyword=' + encodeURIComponent(word);
      var proxyUrl = 'https://corsproxy.io/?' + encodeURIComponent(targetUrl);
      var res = await fetch(proxyUrl);
      
      if (res.ok) {
        var data = await res.json();
        if (data && data.data && data.data.length > 0) {
          var item = data.data[0];
          var japaneseObj = item.japanese[0] || {};
          var kanji = japaneseObj.word || japaneseObj.reading || rawWord;
          var reading = japaneseObj.reading || '';
          
          var senses = item.senses || [];
          var primarySense = senses[0] && senses[0].english_definitions ? senses[0].english_definitions.join(', ') : '';

          var entry = {
            word: rawWord,
            japanese: kanji,
            reading: reading,
            meanings: primarySense,
            examples: [
              {
                jp: kanji + " (" + (reading || kanji) + ")",
                en: "Definition: <span class=\"dict-highlight\">" + primarySense + "</span>"
              }
            ]
          };

          saveCachedResult(word, entry);
          return entry;
        }
      }
    } catch (err) {
      console.log("Online fetch error, using fallback format:", err);
    }

    // Fallback if lookup failed or offline without cache
    var fallbackEntry = {
      word: rawWord,
      japanese: rawWord,
      reading: "―",
      examples: [
        {
          jp: "<span class=\"dict-highlight\">" + rawWord + "</span> の検索結果が見つかりませんでした。",
          en: "No translation cached for <span class=\"dict-highlight\">" + rawWord + "</span>."
        }
      ]
    };
    return fallbackEntry;
  }

  /**
   * Render dictionary details inside modal
   */
  function renderModalContent(data) {
    var modalBody = document.getElementById('dict-modal-body');
    if (!modalBody) return;

    var headingTitle = (data.word || '') + ' (' + (data.japanese || '') + (data.reading ? ' • ' + data.reading : '') + ')';
    
    var html = '<h3 class="dict-header">#' + headingTitle + '</h3>';

    if (data.meanings) {
      html += '<div style="margin-bottom: 12px; font-size: 0.9em; color: #616161;"><strong>Definition:</strong> ' + data.meanings + '</div>';
    }

    if (data.examples && data.examples.length > 0) {
      data.examples.forEach(function(ex) {
        html += '<div class="dict-example-item">';
        html += '  <div class="dict-example-jp">' + ex.jp + '</div>';
        html += '  <div class="dict-example-en">' + ex.en + '</div>';
        html += '</div>';
      });
    } else {
      html += '<div style="color: #888;">No example sentences found.</div>';
    }

    modalBody.innerHTML = html;
  }

  function openModal() {
    var modalOverlay = document.getElementById('dict-modal-overlay');
    if (modalOverlay) {
      modalOverlay.style.display = 'flex';
    }
  }

  function closeModal() {
    var modalOverlay = document.getElementById('dict-modal-overlay');
    if (modalOverlay) {
      modalOverlay.style.display = 'none';
    }
  }

  /**
   * Main function called when user taps a word chip in Search Mode
   */
  async function lookupWord(word) {
    if (!word) return;

    var modalBody = document.getElementById('dict-modal-body');
    if (modalBody) {
      modalBody.innerHTML = '<div style="text-align: center; padding: 24px; color: #757575;">Searching definition for <strong>' + word + '</strong>...</div>';
    }
    openModal();

    var result = await fetchOnlineDefinition(word);
    renderModalContent(result);
  }

  /**
   * Bind event handlers once DOM is ready
   */
  function init() {
    var btnSearch = document.getElementById('btn-search');
    if (btnSearch) {
      btnSearch.onclick = function() {
        toggleSearchMode();
      };
    }

    var btnClose = document.getElementById('dict-modal-close');
    if (btnClose) {
      btnClose.onclick = function() {
        closeModal();
      };
    }

    var modalOverlay = document.getElementById('dict-modal-overlay');
    if (modalOverlay) {
      modalOverlay.onclick = function(e) {
        if (e.target === modalOverlay) {
          closeModal();
        }
      };
    }

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        closeModal();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose module globally for front.html
  window.NarabikaeDict = {
    isSearchModeActive: isSearchModeActive,
    toggleSearchMode: toggleSearchMode,
    lookupWord: lookupWord,
    closeModal: closeModal
  };
})();