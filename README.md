# YouTube Channel Analysis Task

## Description:
it was required to Analyze MBC مصر YouTube channel and provide us with insights on how to enhance this channel's performance.

## Procedure:
### Collecting the channel data:

  This part as done as follows:
  - The channel sections are obtained (if exists), but it is found that MBCمصر channel has no sections.
  - For each channel section, the code obtains its playlists information like playlists title and URL. So, as the channel has no sections, all the created playlists are obtained.
  - For each returned playlist (except the private playlists), the code collects the number of videos, number of views, its videos titles and URLs. At this step we collected all videos in the channel. The result of this step is saved in the excel file ‘Playlists.xlsx’. 
  - Then, for each video the code is scrapping its information like number of like, dislikes, views, publication date, description and so on. The result of this step is saved in the excel file ‘Videos.xlsx’.

### Analyzing the data for insights to enhance the channel's performance
 
#### Analyzing Playlist according to the number of views
   1. Obtaining the top 10 playlists according to the number of views and Obtainig a figure shows the bar chart w.r.t number of views.
   2. Obtaining the Least 10 playlists according to the number of views and Obtaining a figure shows the bar chart w.r.t number of views.

#### Analyzing Playlist according to the number of videos
   1. Obtaining the top 10 playlists according to the number of videos and Obtainig a figure shows the bar chart w.r.t number of videos.
   2. Obtaining the Least 10 playlists according to the number of videos and Obtaining a figure shows the bar chart w.r.t number of videos.
#### Analyzing Videos according to the number of Views (for Least 10 Playlists)
In this section I took the least 10 playlists in view number and searched for the least ten videos in view number, and I obtained:
   1. a figure shows these videos and their corresponding playlist.
   2. two figures show the bar chars of these videos. 
   - Number of views.
   - Number of likes and dislikes.