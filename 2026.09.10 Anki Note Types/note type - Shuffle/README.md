# note type - Shuffle

This note type is suppose to be paired with "only_again" tweak from the mino tweaks addon.

## versions list:

**v8** - this is where I made the narabikae the only_again addon so instead of using pycmd("ease3"); of grading I am using pycmd("mino_rate_good"). I'm planning to implement dummy words and put the first words for quicker reviewing at later version.

**v9** - in this version I implemented dummy words. added a new field called 'dummy' and if it's empty, it defaults to 'english' where it goes to collection.media to find \_dummyWords.json and see what dummy words 'english' adds. if 'dummy' field is not empty like 'welcome, hi, nope' it will make the dummy word choose in that pool. if there is only one dummy word in the field for example 'numbers', it starts looking to \_dummyWords.json to see the set of words of numbers.
