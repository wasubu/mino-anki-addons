// _narabikaeDictionary.js - do not modify nor delete this line - v0
/**
 * _narabikaeDictionary.js
 * Web Search Translation & Offline Cache Module for Anki Sentence Ordering
 */

(function() {
  'use strict';

  var searchModeActive = false;
  var CACHE_PREFIX = 'narabikae_dict_cache_';

  // Offline pre-built fallbacks for common words in case device has no internet on first launch
  var LOCAL_FALLBACKS = {
    "to": {
      word: "To",
      japanese: "〜へ / 〜に",
      reading: "へ / に",
      examples: [
        { jp: "学校<span class=\"dict-highlight\">へ</span>行く", en: "Go <span class=\"dict-highlight\">to</span> school." },
        { jp: "彼<span class=\"dict-highlight\">に</span>話す", en: "Talk <span class=\"dict-highlight\">to</span> him." }
      ]
    },
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
      japanese: "心配して",
      reading: "しんぱいして",
      examples: [
        { jp: "僕は<span class=\"dict-highlight\">心配</span>してた", en: "I was <span class=\"dict-highlight\">worried</span>." },
        { jp: "彼女は<span class=\"dict-highlight\">心配</span>している", en: "She is <span class=\"dict-highlight\">worried</span>." }
      ]
    }
  };

  function isSearchModeActive() {
    return searchModeActive;
  }

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

  function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  }

  function highlightWord(text, target) {
    if (!text || !target) return text;
    var escaped = target.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    var regex = new RegExp('(' + escaped + ')', 'gi');
    return text.replace(regex, '<span class="dict-highlight">$1</span>');
  }

  /**
   * Cache Management (Saves queries locally to collection.media storage)
   */
  function getCachedResult(word) {
    var key = CACHE_PREFIX + cleanWord(word);
    try {
      var cached = localStorage.getItem(key);
      if (cached) {
        return JSON.parse(cached);
      }
    } catch (e) {
      console.warn("Cache read error:", e);
    }
    return null;
  }

  function saveCachedResult(word, data) {
    var key = CACHE_PREFIX + cleanWord(word);
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
      console.warn("Cache write error:", e);
    }
  }

  /**
   * Online Translation Fetch (MyMemory API - Native CORS support, EN to JA)
   */
  async function fetchOnlineDefinition(rawWord) {
    var word = cleanWord(rawWord);
    if (!word) return null;

    // 1. Check local offline cache first
    var cached = getCachedResult(word);
    if (cached) return cached;

    // 2. Fetch live translation and example sentence matches from the Web
    try {
      var apiUrl = 'https://api.mymemory.translated.net/get?q=' + encodeURIComponent(rawWord) + '&langpair=en|ja';
      var res = await fetch(apiUrl);

      if (res.ok) {
        var data = await res.json();
        if (data && data.responseData && data.responseData.translatedText) {
          var mainTranslation = data.responseData.translatedText;
          var examples = [];

          // Extract translation memory matches for example sentences
          if (Array.isArray(data.matches)) {
            var seen = new Set();
            for (var i = 0; i < data.matches.length; i++) {
              var m = data.matches[i];
              var enText = (m.segment || '').trim();
              var jpText = (m.translation || '').trim();

              if (enText && jpText && enText.toLowerCase() !== jpText.toLowerCase() && !seen.has(enText.toLowerCase())) {
                seen.add(enText.toLowerCase());

                var highlightedEn = highlightWord(enText, rawWord);
                var highlightedJp = highlightWord(jpText, mainTranslation);

                examples.push({
                  jp: highlightedJp,
                  en: highlightedEn
                });

                if (examples.length >= 3) break;
              }
            }
          }

          if (examples.length === 0) {
            examples.push({
              jp: "<span class=\"dict-highlight\">" + mainTranslation + "</span>",
              en: "<span class=\"dict-highlight\">" + rawWord + "</span>"
            });
          }

          var entry = {
            word: capitalize(rawWord),
            japanese: mainTranslation,
            reading: "",
            examples: examples
          };

          // Save to local cache for instant offline reuse
          saveCachedResult(word, entry);
          return entry;
        }
      }
    } catch (err) {
      console.warn("Live web lookup failed, falling back:", err);
    }

    // 3. Check built-in fallbacks if offline
    if (LOCAL_FALLBACKS[word]) {
      var fallback = LOCAL_FALLBACKS[word];
      saveCachedResult(word, fallback);
      return fallback;
    }

    // 4. Default notice if completely offline without cache
    return {
      word: capitalize(rawWord),
      japanese: rawWord,
      reading: "",
      examples: [
        {
          jp: "<span class=\"dict-highlight\">" + rawWord + "</span> の検索結果が見つかりませんでした。",
          en: "Could not retrieve online translation for <span class=\"dict-highlight\">" + rawWord + "</span>."
        }
      ]
    };
  }

  /**
   * Modal Display Handler
   */
  function renderModalContent(data) {
    var modalBody = document.getElementById('dict-modal-body');
    if (!modalBody) return;

    var headerText = data.word + ' (' + data.japanese + (data.reading ? ' • ' + data.reading : '') + ')';
    
    var html = '<h3 class="dict-header">#' + headerText + '</h3>';

    if (data.examples && data.examples.length > 0) {
      data.examples.forEach(function(ex) {
        html += '<div class="dict-example-item">';
        html += '  <div class="dict-example-jp">' + ex.jp + '</div>';
        html += '  <div class="dict-example-en">' + ex.en + '</div>';
        html += '</div>';
      });
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

  window.NarabikaeDict = {
    isSearchModeActive: isSearchModeActive,
    toggleSearchMode: toggleSearchMode,
    lookupWord: lookupWord,
    closeModal: closeModal
  };
})();