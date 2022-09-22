# ADAM-Parser
This script is used to create a logged in adam session and fetch all your courses and course files for the current semester.

In order to use it, you must create a userdata.txt in the following style

userdata.txt
```
youremail@unibas.ch
adampassword
/path/to/course/directory
```

My userdata.txt would look like this:
```
julian.bopp@unibas.ch
notmyrealpasswordofcourse
/home/julian/UNIBAS/9 HS 2022/
```

## What I still need/want to add:
- Some courses use external pages, different from ADAM, to upload their lecture slides or exercise sheets. I'd like to use this script to download these files aswell
- Some exercise sheets come with additional resources. Currently all resources and exercise sheets will be downloaded to one folder. I'd like the script to create a folder for each exercise that separates the exercise resources from eachother like so:

- sheet01 -> sheet01.pdf, sheet01resources.zip
- sheet02 -> sheet01.pdf, sheet01resources.zip
...

