# note type - Shuffle

This note type is suppose to be paired with "only_again" tweak from the mino tweaks addon.

## note type version list:

**v8** - this is where I made the narabikae the only_again addon so instead of using pycmd("ease3"); of grading I am using pycmd("mino_rate_good"). I'm planning to implement dummy words and put the first words for quicker reviewing at later version.

**v9** - Implemented dummy words. added a new field called 'dummy' and if it's empty, it defaults to 'english' where it goes to collection.media to find \_dummyWords.json and see what dummy words 'english' adds. if 'dummy' field is not empty like 'welcome, hi, nope' it will make the dummy word choose in that pool. if there is only one dummy word in the field for example 'numbers', it starts looking to \_dummyWords.json to see the set of words of numbers.

**v10** - I made it so that the last correct sentence word is now automatically added to the input box if the word count is 6 or more. if the word count is 5 or less then dummy text should be two. also the automatic last word has this cool animation.

**v11** - I added the word timing feature. where in the field {{Timing}} I can add something like "300, 400, 600, 100" where the numbers are in ms and represents the interval bewteen words. for example "I love you too" with those numbers, 300 will be the interval from the start of the audio to the word "I" and 400 is interval from "I" to "love". also improved the animation from the start of front to be invisible to the mouse and bigger and slower animations. the back.html is kinda bloated so I moved styles to the main css.
Hopefully I can make a tool to make these Timing numbers faster.

## Anki Video Optimizer.ahk version list:

**v1** - this ahk script will make the video you put downsize to 720, compress it, and make an Anki-friendly MP4.

**v2** - Instead of saving it to mp4, it saves to .webm file, It also uses VP9 for video and Opus for audio.
