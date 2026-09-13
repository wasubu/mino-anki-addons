// _narabikaeDictionary.js - do not modify nor delete this line - v6
/**
 * _narabikaeDictionary.js
 * Dictionary Lookup & Offline Caching Module for Anki Sentence Ordering
 * Powered by Jotoba API (Sentence Pairs) & Google GTX (Translation & Furigana)
 */

(function() {
  'use strict';

  // --- CONFIGURATION ---
  var enableClearCache = false; // Set to true to clear dictionary cache on every script load
  var CACHE_PREFIX = 'narabikae_dict_cache_';
  var searchModeActive = false;

  // Offline built-in fallbacks for common words
  var LOCAL_FALLBACKS = {
    "see": {
      word: "See",
      japanese: "見る",
      reading: "みる",
      examples: [
        { jp: "僕はそれを<span class=\"dict-highlight\">見</span>た", en: "I <span class=\"dict-highlight\">saw</span> it." },
        { jp: "また明日お会いしましょう", en: "I hope to <span class=\"dict-highlight\">see</span> you tomorrow." }
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
    "to": {
      word: "To",
      japanese: "〜へ",
      reading: "へ",
      examples: [
        { jp: "学校<span class=\"dict-highlight\">へ</span>行く", en: "Go <span class=\"dict-highlight\">to</span> school." },
        { jp: "彼<span class=\"dict-highlight\">に</span>話す", en: "Talk <span class=\"dict-highlight\">to</span> him." }
      ]
    }
  };

  /**
   * Helper to check if a Japanese text contains Kanji
   */
  function containsKanji(str) {
    if (!str) return false;
    return /[\u4e00-\u9faf\u3400-\u4dbf]/.test(str);
  }

  /**
   * Inject CSS for sticky header, vertical scrolling, and scroll-containment
   */
  function injectStyles() {
    if (document.getElementById('narabikae-dict-styles')) return;
    var style = document.createElement('style');
    style.id = 'narabikae-dict-styles';
    style.textContent = [
      '#dict-modal-overlay {',
      '  overscroll-behavior: contain;',
      '}',
      '#dict-modal-body {',
      '  max-height: 70vh;',
      '  overflow-y: auto;',
      '  overflow-x: hidden;',
      '  position: relative;',
      '  box-sizing: border-box;',
      '  overscroll-behavior: contain;',
      '}',
      '.dict-header {',
      '  position: sticky;',
      '  top: 0;',
      '  background: #ffffff;',
      '  padding: 12px 0;',
      '  margin: 0 0 12px 0;',
      '  z-index: 10;',
      '  border-bottom: 1px solid #e0e0e0;',
      '  word-break: break-word;',
      '}',
      '@media (prefers-color-scheme: dark) {',
      '  .dict-header {',
      '    background: #2d2d2d;',
      '    color: #ffffff;',
      '    border-bottom-color: #444444;',
      '  }',
      '}'
    ].join('\n');
    document.head.appendChild(style);
  }

  /**
   * Enhanced Romaji to Hiragana Transliteration Engine
   */
  function romajiToHiragana(romaji) {
    if (!romaji) return '';
    if (/[\u3040-\u30ff\u4e00-\u9faf]/.test(romaji)) return romaji;

    var str = romaji.toLowerCase().trim();

    // Normalize Hepburn macrons & symbols
    str = str
      .replace(/[āâ]/g, 'aa')
      .replace(/[īî]/g, 'ii')
      .replace(/[ūû]/g, 'uu')
      .replace(/[ēê]/g, 'ee')
      .replace(/[ōô]/g, 'ou')
      .replace(/['\-]/g, '');

    var map = {
      'a':'あ','i':'い','u':'う','e':'え','o':'お',
      'ka':'か','ki':'き','ku':'く','ke':'け','ko':'こ',
      'sa':'さ','shi':'し','su':'す','se':'せ','so':'そ',
      'ta':'た','chi':'ち','tsu':'つ','te':'て','to':'と',
      'na':'な','ni':'に','nu':'ぬ','ne':'ね','no':'の',
      'ha':'は','hi':'ひ','fu':'ふ','he':'へ','ho':'ほ',
      'ma':'ま','mi':'み','mu':'む','me':'め','mo':'も',
      'ya':'や','yu':'ゆ','yo':'よ',
      'ra':'ら','ri':'り','ru':'る','re':'れ','ro':'ろ',
      'wa':'わ','wo':'を','n':'ん','nn':'ん',
      'ga':'が','gi':'ぎ','gu':'ぐ','ge':'げ','go':'ご',
      'za':'ざ','ji':'じ','zu':'ず','ze':'ぜ','zo':'ぞ',
      'da':'だ','dji':'ぢ','dzu':'づ','de':'で','do':'ど',
      'ba':'ば','bi':'び','bu':'ぶ','be':'べ','bo':'ぼ',
      'pa':'ぱ','pi':'ぴ','pu':'ぷ','pe':'ぺ','po':'ぽ',
      'kya':'きゃ','kyu':'きゅ','kyo':'きょ',
      'sha':'しゃ','shu':'しゅ','sho':'しょ',
      'cha':'ちゃ','chu':'ちゅ','cho':'ちょ',
      'nya':'にゃ','nyu':'にゅ','nyo':'にょ',
      'hya':'ひゃ','hyu':'ひゅ','hyo':'ひょ',
      'mya':'みゃ','myu':'みゅ','myo':'みょ',
      'rya':'りゃ','ryu':'りゅ','ryo':'りょ',
      'gya':'ぎゃ','gyu':'ぎゅ','gyo':'ぎょ',
      'ja':'じゃ','ju':'じゅ','jo':'じょ',
      'bya':'びゃ','byu':'びゅ','byo':'びょ',
      'pya':'ぴゃ','pyu':'ぴゅ','pyo':'ぴょ'
    };

    var res = '';
    var i = 0;
    while (i < str.length) {
      if (i + 1 < str.length && str[i] === str[i+1] && /[bcdfghjklmpqrstvwxyz]/.test(str[i]) && str[i] !== 'n') {
        res += 'っ';
        i++;
        continue;
      }

      var match = false;
      for (var len = 3; len >= 1; len--) {
        var chunk = str.substr(i, len);
        if (map[chunk]) {
          res += map[chunk];
          i += len;
          match = true;
          break;
        }
      }
      if (!match) {
        i++;
      }
    }
    return res;
  }

  function clearCache() {
    try {
      var keysToRemove = [];
      for (var i = 0; i < localStorage.length; i++) {
        var key = localStorage.key(i);
        if (key && key.indexOf(CACHE_PREFIX) === 0) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(function(k) {
        localStorage.removeItem(k);
      });
      console.log("[NarabikaeDict] Cache cleared (" + keysToRemove.length + " items removed)");
    } catch (e) {
      console.warn("Cache clear error:", e);
    }
  }

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
    return (w || '').trim().toLowerCase().replace(/^[^\w]+|[^\w]+$/g, '').replace(/[^\w]/g, '');
  }

  function sanitizeWord(str) {
    return (str || '').replace(/^[^\w]+|[^\w]+$/g, '').trim();
  }

  function capitalize(str) {
    if (!str) return '';
    var s = sanitizeWord(str);
    return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
  }

  function decodeHTMLEntities(str) {
    if (!str) return '';
    var txt = document.createElement('textarea');
    txt.innerHTML = str;
    return txt.value;
  }

  function highlightWord(text, target) {
    if (!text || !target) return text;
    var cleanTarget = target.replace(/[()\[\]{}~]/g, '').trim();
    if (!cleanTarget) return text;

    var escaped = cleanTarget.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    var regex = new RegExp('(' + escaped + ')', 'gi');
    return text.replace(regex, '<span class="dict-highlight">$1</span>');
  }

  function isValidExamplePair(en, jp) {
    if (!en || !jp) return false;
    if (en.toLowerCase() === jp.toLowerCase()) return false;
    if (/http|www\.|tatoeba|warning|quality/i.test(en + jp)) return false;
    if (en.length > 140 || jp.length > 140) return false;
    if (en.length < 3 || jp.length < 1) return false;
    return true;
  }

  function fetchWithTimeout(url, options, timeoutMs) {
    if (typeof options === 'number') {
      timeoutMs = options;
      options = {};
    }
    options = options || {};
    var ms = timeoutMs || 3500;

    return new Promise(function(resolve, reject) {
      var timer = setTimeout(function() {
        reject(new Error("Request timed out"));
      }, ms);

      fetch(url, options)
        .then(function(res) {
          clearTimeout(timer);
          resolve(res);
        })
        .catch(function(err) {
          clearTimeout(timer);
          reject(err);
        });
    });
  }

  /**
   * Fetch sentence data from Jotoba API (Native CORS)
   */
  async function fetchJotobaData(cleanWord) {
    var jotobaUrl = 'https://jotoba.de/api/search/sentences';
    
    try {
      var res = await fetchWithTimeout(jotobaUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: cleanWord,
          language: "English"
        })
      }, 3500);

      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn("Jotoba fetch error:", e);
    }

    return null;
  }

  /**
   * Online Fetch: Google GTX (Translation & Reading) + Jotoba API (Sentence Pairs)
   */
  async function fetchOnlineDefinition(rawWord) {
    var clean = cleanWord(rawWord);
    if (!clean) return null;

    if (!enableClearCache) {
      var cached = getCachedResult(clean);
      if (cached) return cached;
    }

    var displayWord = capitalize(rawWord);
    var japaneseKanji = "";
    var japaneseReading = "";
    var examples = [];

    var gtxUrl = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ja&dt=t&dt=rm&q=' + encodeURIComponent(clean);

    try {
      var results = await Promise.allSettled([
        fetchWithTimeout(gtxUrl, 3500),
        fetchJotobaData(clean)
      ]);

      // Process Google GTX Translation & Furigana
      if (results[0].status === 'fulfilled' && results[0].value && results[0].value.ok) {
        try {
          var gtxData = await results[0].value.json();
          if (gtxData && gtxData[0] && gtxData[0][0]) {
            japaneseKanji = gtxData[0][0][0] || "";

            if (gtxData[0][1] && gtxData[0][1][2]) {
              var romaji = gtxData[0][1][2];
              japaneseReading = romajiToHiragana(romaji);
            }
          }
        } catch (e) {
          console.warn("Google GTX parse error:", e);
        }
      }

      // Process Jotoba Sentence Pairs (max 6)
      if (results[1].status === 'fulfilled' && results[1].value) {
        try {
          var jotobaData = results[1].value;
          var sentences = (jotobaData && jotobaData.sentences) ? jotobaData.sentences : [];
          var seen = new Set();

          for (var i = 0; i < sentences.length; i++) {
            var item = sentences[i];
            var rawJp = item.content || item.japanese || '';
            var enText = decodeHTMLEntities(item.translation || item.english || '').trim();

            var jpText = decodeHTMLEntities(rawJp.replace(/\[([^|\]]+)\|?[^\]]*\]/g, '$1')).trim();

            if (isValidExamplePair(enText, jpText) && !seen.has(enText.toLowerCase())) {
              seen.add(enText.toLowerCase());

              examples.push({
                jp: highlightWord(jpText, japaneseKanji),
                en: highlightWord(enText, clean)
              });
            }
            if (examples.length >= 6) break;
          }
        } catch (e) {
          console.warn("Jotoba parse error:", e);
        }
      }
    } catch (err) {
      console.warn("API Fetch Error:", err);
    }

    // Fallback if translation API failed
    if (!japaneseKanji) {
      if (LOCAL_FALLBACKS[clean]) {
        var fb = LOCAL_FALLBACKS[clean];
        saveCachedResult(clean, fb);
        return fb;
      }
      japaneseKanji = displayWord;
    }

    // Prevent duplicate reading or showing reading when no kanji is present
    if (japaneseKanji === japaneseReading || !containsKanji(japaneseKanji)) {
      japaneseReading = "";
    }

    var entry = {
      word: displayWord,
      japanese: japaneseKanji,
      reading: japaneseReading,
      examples: examples
    };

    saveCachedResult(clean, entry);
    return entry;
  }

  /**
   * Render Modal Header Layout & Examples
   */
  function renderModalContent(data) {
    var modalBody = document.getElementById('dict-modal-body');
    if (!modalBody) return;

    var engText = data.word || '';
    var kanjiText = data.japanese || '';
    var readingText = containsKanji(kanjiText) ? (data.reading || '') : '';

    var headerText = engText;

    if (kanjiText && readingText && kanjiText !== readingText) {
      headerText += ' (' + kanjiText + ' • ' + readingText + ')';
    } else if (kanjiText) {
      headerText += ' (' + kanjiText + ')';
    }

    var html = '<h3 class="dict-header">' + headerText + '</h3>';
    html += '<div id="dict-examples-list"></div>';
    modalBody.innerHTML = html;

    var listEl = document.getElementById('dict-examples-list');
    var examples = data.examples || [];

    if (examples.length === 0) {
      if (listEl) {
        listEl.innerHTML = '<div style="text-align: center; color: #888; font-style: italic; margin-top: 16px;">No example sentences found on Jotoba.</div>';
      }
      return;
    }

    // Batch 1: Render first 3 examples immediately
    var firstBatch = examples.slice(0, 3);
    var batch1Html = '';
    firstBatch.forEach(function(ex) {
      batch1Html += '<div class="dict-example-item">';
      batch1Html += '  <div class="dict-example-jp">' + ex.jp + '</div>';
      batch1Html += '  <div class="dict-example-en">' + ex.en + '</div>';
      batch1Html += '</div>';
    });
    listEl.innerHTML = batch1Html;

    // Batch 2: Render remaining examples (up to 6 total) after brief delay
    if (examples.length > 3) {
      setTimeout(function() {
        var secondBatch = examples.slice(3, 6);
        var batch2Html = '';
        secondBatch.forEach(function(ex) {
          batch2Html += '<div class="dict-example-item">';
          batch2Html += '  <div class="dict-example-jp">' + ex.jp + '</div>';
          batch2Html += '  <div class="dict-example-en">' + ex.en + '</div>';
          batch2Html += '</div>';
        });
        if (listEl) {
          listEl.insertAdjacentHTML('beforeend', batch2Html);
        }
      }, 100);
    }
  }

  function openModal() {
    var modalOverlay = document.getElementById('dict-modal-overlay');
    if (modalOverlay) {
      modalOverlay.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }
  }

  function closeModal() {
    var modalOverlay = document.getElementById('dict-modal-overlay');
    if (modalOverlay) {
      modalOverlay.style.display = 'none';
      document.body.style.overflow = '';
    }
  }

  async function lookupWord(word) {
    if (!word) return;

    // Turn off Search Mode when a word is clicked
    if (searchModeActive) {
      toggleSearchMode();
    }

    var clean = sanitizeWord(word);
    var modalBody = document.getElementById('dict-modal-body');
    if (modalBody) {
      modalBody.innerHTML = '<div style="text-align: center; padding: 24px; color: #757575;">Searching definition for <strong>' + clean + '</strong>...</div>';
    }
    openModal();

    var result = await fetchOnlineDefinition(clean);
    renderModalContent(result);
  }

  function init() {
    injectStyles();

    if (enableClearCache) {
      clearCache();
    }

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
    closeModal: closeModal,
    clearCache: clearCache
  };
})();