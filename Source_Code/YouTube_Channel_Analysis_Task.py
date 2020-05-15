# Importing required libraries
from bs4 import BeautifulSoup
import re
import requests
import time
from selenium import webdriver
import pandas as pd
import matplotlib.pyplot as plt

# Defining the global variables
wait_between_requests = 3
channel_name = 'CBCEgypt'
youtube_base = 'https://www.youtube.com/'
parent_folder = ''  # users or channel or empty
selenium_driver_path= r'C:\Users\SMSM-TECH\Downloads\chromedriver_win32\chromedriver.exe'

# get selenium driver object
def get_selenium_driver():
    """
    This function returns the selenium driver object.
    Parameters:
        None
    Returns:
        driver: selenium driver object
    """
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(executable_path = selenium_driver_path, options = options)
    return driver


def scroll_to_end(driver):
  """
    This function Scroll the page to the end.
    Parameters:
         driver: selenium driver object
    Returns:
        innerHTML : The page HTML source after scrolling 
        """
  SCROLL_PAUSE_TIME = 7
  last_height = driver.execute_script("return document.documentElement.scrollHeight")
  while True:
    # Scroll down to bottom
        driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
    # Wait to load page
        
        time.sleep(SCROLL_PAUSE_TIME)
    # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
           break
        else:
           last_height = new_height
  innerHTML = driver.execute_script("return document.body.innerHTML")
  return innerHTML

def get_soup(url, driver):
    """
    Given the url of a page and the driver object (to scroll to end) ,
    this function returns the soup object.   
    Parameters:
        url: the link to get soup object for
        driver: selenium driver object
    Returns:
        soup: soup object
    """
    
    driver.get(url)
    driver.implicitly_wait(wait_between_requests)
    html = scroll_to_end(driver)
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def fix_url(url): 
    """
    This function correctS relative urls back to absolute urls   
    Parameters:
        url: the link to check if absolute or relative
    Returns:
        url: absolute after correction
    """
    if url[0] == '/':
        return youtube_base + url
    else:
        return url

def get_sections(driver):
  """
    This function gets the sections of the channel if exists   
    Parameters:
        driver: selenium driver object to be passed to get_soup
    Returns:
        sections_info: list of dictionaries of all sections informations(title,link)
    """    
  global parent_folder
  soup = get_soup(f'{youtube_base}/user/{channel_name}/playlists', driver)

  if soup is None or 'This channel does not exist.' in soup.text:
        url = f'{youtube_base}/channel/{channel_name}/playlists'
        
        soup = get_soup(url, driver)
        if soup is None or 'This channel does not exist.' in soup.text:
            raise ValueError('The channel does not exists: ' + channel_name)
        parent_folder = 'channel/'
        
  sections_atags = soup.find_all('a', {'href': re.compile(f'{channel_name}/playlists')})
  # filter out non user playlists next
  sections_info = [{'title': x.text.strip(), 'link': fix_url(x['href'])} for x in sections_atags
                    if x.span and ('shelf_id=0' not in x['href'])]

  # no sections, make up no sections section with default link
  if len(sections_info) == 0:
    url = f'{youtube_base}{parent_folder}{channel_name}/playlists'
    sections_info = [ {'title': 'no sections', 'link': url}]

  return sections_info   

 
def get_all_playlists(section, driver):
   """
    This function gets all playlists of a channel section if exists   
    Parameters:
        section: Dictioary contains information of the section(title,link)
        driver: selenium driver object to be passed to get_soup
    Returns:
        playlists_info: list of dictionaries of all section playlists informations
        (section title,playlist title ,playlist link)
    """     
   global parent_folder
   soup = get_soup(section['link'], driver)
   playlists_tags = soup.find_all( id= 'video-title' )
   playlists_info = []
   for a in playlists_tags:  # find title and link
        title = a.text
        if title != 'Liked videos': # skip these
            url = fix_url(a['href'])
            url = url.replace('watch','playlist')
            playlists_info.append({ 'section title' : section['title'],'playlist title': title, 'playlist link': url})

   if not playlists_info:  # no playlists return default link 
        url = f'{youtube_base}/{parent_folder}{channel_name}/videos'
        playlists_info = [{ 'section title' : section['title'], 'playlist title': 'No Playlists', 
                           'playlist link': url}]
   return playlists_info 

def get_playlist_info(playlist, driver):
   """
    This function gets all Videos and information of a playlist if exists   
    Parameters:
        playlist: Dictioary contains information of the playlist
        (section title,playlist title ,playlist link)
        driver: selenium driver object to be passed to get_soup
    Returns:
        videos_info: list of dictionaries of all videos in the palylist and info
        (section title, playlist title,playlist videos_num, playlist views_num,
        playlist last_update, video title,video link)
    """     
   playlist_link= playlist['playlist link']
   soup = get_soup(playlist_link, driver)

   ##channel titles,videos no,views ,last updated
   PL_info = soup.find_all('yt-formatted-string', class_='style-scope ytd-playlist-sidebar-primary-info-renderer')
   PL_videos_no = PL_info[1].text
   PL_views_no = PL_info[2].text
   PL_last_update = PL_info[3].text
   ##titles, summery
   videos_titles = soup.find_all( id= 'video-title' )
   ##links of videos
   atags_videos = soup.find_all('a', class_='yt-simple-endpoint style-scope ytd-playlist-video-renderer' )
   videos_info=[]
   i=0
   for a in atags_videos:  # find title and link
        url = fix_url(a['href'])
        videos_info.append({ 'section title' : playlist['section title'], 'playlist title': playlist['playlist title'],'videos_num':PL_videos_no,'views_num':PL_views_no,'last_update' : PL_last_update, 
                            'video title': videos_titles[i]['title'],'video link' : url})
        i=i+1
   if not videos_info:  # no playlists)
     url = playlist_link
     videos_info = [{'section title' : playlist['section title'],'playlist title': playlist['playlist title'],'videos_num':PL_videos_no,
                     'views_num':PL_views_no, 'last_update' : PL_last_update, 'video title': 'No Videos', 'video link': url}]  
   return videos_info
   

def scrap_video(video):
    """
    This function get information of a Video    
    Parameters:
        playlist: Dictioary contains information of the video
        (section title, playlist title,playlist videos_num, playlist views_num,
        playlist last_update, video title,video link)
    
    Returns:
        d: Dictionary of video information
        ( playlist title,video title,video link, Video views, Video short_link,
        Video likes,Video dislikes, video publication_date, Video description )
    """     
    d = {'Playlist title' : video['playlist title'], 'Video link': video['video link'], 'Video views': None, 'Video short_link': video['video link'],
         'Video likes': None, 'Video dislikes': None}

    # now get video page and pull information from it
    content = requests.get(video['video link'])
    # create beautiful soup object to parse HTML
    vsoup = BeautifulSoup(content.content, "html.parser")

    o = vsoup.find('title')
    vtitle = o.text.strip()
    xending = ' - YouTube'
    d['Video title'] = vtitle[:-len(xending)] \
        if vtitle.endswith(xending) else vtitle

    # o is used in the code following to
    # catch missing data targets for scrapping
    o = vsoup.find('div', class_='watch-view-count')
    if o:
        views = o.text
        d['Video views'] = ''.join(c for c in views if c in '0123456789')

    o = vsoup.find('strong', class_='watch-time-text')
    d['publication_date'] = \
        o.text[len('Published on ') - 1:] if o else ''

    o = vsoup.find('div', id='watch-description-text')
    d['Video description'] = o.text if o else ''

    o = vsoup.find('meta', itemprop='videoId')
    if o:
        vid = o['content']
        d['Video short_link'] = f'https://youtu.be/{vid}'

    o = vsoup.find('button',
                   class_='like-button-renderer-like-button')
    if o:
        o = o.find('span', class_='yt-uix-button-content')
        d['Video likes'] = o.text if o else ''

    o = vsoup.find('button',
                   class_='like-button-renderer-dislike-button')
    if o:
        o = o.find('span', class_='yt-uix-button-content')
        d['Video dislikes'] = o.text if o else ''

    return d


def scrap_video_list(video_list):
    """
    This function get information of all Video in a list   
    Parameters:
        video_list: list of Dictioaries contain information of each video
        (section title, playlist title,playlist videos_num, playlist views_num,
        playlist last_update, video title,video link)
    
    Returns:
        scraped_data_list: list of Dictioaries of videos information
        ( playlist title,video title,video link, Video views, Video short_link,
        Video likes,Video dislikes, video publication_date, Video description )
    """     
    scraped_data_list=[]
    for i in range(len(video_list)):
        scraped_data_list.append(scrap_video(video_list[i]))
    return scraped_data_list
  
###################################################################################
  
driver = get_selenium_driver()
# Obtaining Sections of the channel
Sections =  get_sections(driver)

# Obtaining Playlists Links in all sections of the channel
if ((len(Sections) == 1) and (Sections[0]['title']=='no sections')):# NO sections
    print('NO sections\n')
    print('Getting all created playlists')
    section = Sections[0]
    playlists_ = get_all_playlists(section, driver)
else:
  playlists_ = []
  for section in Sections:
     print(f"Getting playlists for section: {section['title']}")
     playlists_.append(get_all_playlists(section, driver) )
     
# Converting into Dataframe
playlists_df = pd.DataFrame( playlists_)
# Saving into excel
playlists_df.to_excel('Playlists.xlsx', index = False)

# Obtaining ALL videos information (except private playlists)  
Videos_ =[]     
for playlist in playlists_:
   pr_list=['Private - شهر فبراير 2014','private - شهر إبريل 2014','Private - إبريل 2014','prv شهر يناير 2015','private | شهر نوفمبر','مايو 2014 - Praivte']
   if playlist['playlist title'] in pr_list:
       continue
   else:
     returned_list = get_playlist_info(playlist, driver)
     for l in range(len(returned_list)):
        Videos_.append(returned_list[l] )
        
# Converting into Dataframe        
videos_df = pd.DataFrame( Videos_)
# Saving into excel
videos_df.to_excel('Videos.xlsx', index = False)
driver.close()

#################################################################################3
# Analyzing Playlist according to the number of Views and videos
playlist_analyze = videos_df[['playlist title','videos_num','views_num']]
playlist_analyze.drop_duplicates( keep = 'first', inplace = True)
playlist_analyze =playlist_analyze.reset_index(drop = True) 
playlist_analyze['videos_num'] = playlist_analyze['videos_num'].apply(lambda x: int(x.replace(',','').split()[0] ))
playlist_analyze['views_num'] = playlist_analyze['views_num'].apply(lambda x: int(x.replace(',','').split()[0] ))

#Analyzing Playlist according to the number of Views
print('Anayzing Playlist according to the number of Views\n')

print('The top 10 Playlists according to the number of Views are\n' )
top_10_in_views = playlist_analyze.nlargest(10, 'views_num').reset_index(drop = True) 
i = 1
for p in top_10_in_views.to_dict('records'):
  print('The playlist no.' , i , 'is' , p['playlist title'], 'with ',  p['views_num'], ' views' )
  i=i+1
print('\n')  
print('The least 10 Playlists according to the number of Views are\n' ) 
least_10_in_views= playlist_analyze.nsmallest(10, 'views_num').reset_index(drop = True) 
i = 1
for p in least_10_in_views.to_dict('records'):
  print('The playlist no.' , i , 'is' , p['playlist title'], 'with ',  p['views_num'], ' views' )
  i=i+1
print('\n')  

# Analyzing Playlist according to the number of Videos
print('Anayzing Playlist according to the number of Videos\n')

print('The top 10 Playlists according to the number of Videos are\n' )  
top_10_in_videos = playlist_analyze.nlargest(10, 'videos_num').reset_index(drop = True) 
i = 1
for p in top_10_in_videos.to_dict('records'):
  print('The playlist no.' , i , 'is' , p['playlist title'], 'with ',  p['videos_num'], ' videos' )
  i=i+1
print('\n')  
print('The least 10 Playlists according to the number of Videos are\n' )
least_10_in_videos =playlist_analyze.nsmallest(10, 'videos_num').reset_index(drop = True)
i = 1
for p in least_10_in_videos.to_dict('records'):
  print('The playlist no.' , i , 'is' , p['playlist title'], 'with ',  p['videos_num'], ' videos' )
  i=i+1 
############################################################
# Bar charts  
ax1= top_10_in_views.plot.barh(y='views_num')
plt.title('Top 10 Playlists according to the number of Views')
plt.xlabel("Views No.")
plt.ylabel("Playlist Index")

ax2= least_10_in_views.plot.barh(y='views_num')
plt.title('Least 10 Playlists according to the number of Views')
plt.xlabel("Views No.")
plt.ylabel("Playlist Index")

ax3= top_10_in_videos.plot.barh(y='videos_num')
plt.title('Top 10 Playlists according to the number of Videos')
plt.xlabel("Videos No.")
plt.ylabel("Playlist Index")

ax4= least_10_in_videos.plot.barh(y='videos_num')
plt.title('Least 10 Playlists according to the number of Videos')
plt.xlabel("Videos No.")
plt.ylabel("Playlist Index")

######################################################################
# Obtaining the Videos of the top 10 playlists
top_10=[]
for element in top_10_in_views.to_dict('records'):  
    for video in Videos_:
          if video['playlist title'] == element['playlist title']:
             top_10.append(video)   
top_10_DF = pd.DataFrame(top_10) 
top_10_DF.to_excel('Top10_playlists_videos.xlsx', index= False)  

# Obtaining the Videos of the least 10 playlists
least_10=[]
for element in least_10_in_views.to_dict('records'):   
       for video in Videos_:
          if video['playlist title'] == element['playlist title']:
             least_10.append(video) 
  
least_10_DF = pd.DataFrame(least_10) 
least_10_DF.to_excel('Least10_playlists_videos.xlsx', index= False)        

#################################################################
#Analyzing Videos according to the number of Views (Least 10 Playlists)

#Scrapping the Videos of the least 10 playlists
print('Scrapping the Videos of the least 10 playlists in number of views')            
print('\n')
least10_data = scrap_video_list(least_10)
#convert into dataframe
least10_data=pd.DataFrame(least10_data)
#save into excel
least10_data.to_excel('Least10_Videos_scrapped.xlsx', index = False)
print('\n')

print('Anayzing Videos according to the number of Views (Least 10 Playlists)\n')
Least10_analyze = least10_data[['Playlist title','Video title','Video views','Video likes','Video dislikes']]
Least10_analyze.drop_duplicates( keep = 'first', inplace = True)
Least10_analyze =Least10_analyze.reset_index(drop = True) 
Least10_analyze['Video views'] = Least10_analyze['Video views'].apply(lambda x: int(x.replace(',','') ))
Least10_analyze['Video likes'] = Least10_analyze['Video likes'].apply(lambda x: int(x.replace(',','') ))
Least10_analyze['Video dislikes'] = Least10_analyze['Video dislikes'].apply(lambda x: int(x.replace(',','') ))

# Printing the least 10 videos in no.of views
Least_10_videoview = Least10_analyze.nsmallest(10, 'Video views').reset_index(drop = True)
print('The least 10 Videos according to the number of Views are\n' )
i = 1
for p in Least_10_videoview.to_dict('records'):
  print('The Video no.' , i , 'is' , p['Video title'], 'with ',
        p['Video views'], ' views, ' ,
        p['Video likes'], ' likes, ',
        p['Video dislikes'], ' dislikes in Playlist ', p['Playlist title'] )
  i=i+1
# Bar Charts  
ax1= Least_10_videoview[['Video title','Video views']].plot.barh()
plt.title('The Least 10 Videos according to the number of Views')
plt.ylabel("Playlist Index") 

ax2= Least_10_videoview[['Video title','Video likes','Video dislikes']].plot.barh()
plt.title('The Least 10 Videos according to the number of Views')
plt.ylabel("Playlist Index") 

