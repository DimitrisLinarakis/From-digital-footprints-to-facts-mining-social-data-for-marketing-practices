import scrapy
import json
import re
from urllib.parse import urlencode
from datetime import datetime
from ..tools.documents_exporter import DocumentsExporter
from ..items import PersonalInfo
from ..items import SlideShow
from ..items import SlidePost
from ..items import UserData
from ..items import RegularPost


class InstagramSpider(scrapy.Spider):
    name = 'InstagramSpider'
    allowed_domains = ['instagram.com']

    #Populate users_to_scrape from database
    users_to_scrape = []
    for item in list(DocumentsExporter.findDocuments(DocumentsExporter,{}, None, 0, 1)):
        users_to_scrape.append(item["personal_info"]["user_name"])

    #Populate users_to_scrape from file
    #file_directory="C:\\Users\\steve\\OneDrive\\Υπολογιστής\\Πτυχιακή\\InstagramScraperGit\\instascraper\\resources\\BusinessProfiles.json"
    #with open(file_directory,encoding='utf8') as json_file:
    #    data=json.load(json_file)
    #    for channel in data["Profiles"]:
    #        if channel["Id"]!="None" and not list(DocumentsExporter.findDocuments(DocumentsExporter,{"personal_info.user_name":channel["Id"]},{"_id":1},None,None)):
    #            users_to_scrape.append(channel["Id"])

    scraped_users = []
    followers_limit = 1000
    mozilla_cookies = "ig_cb=1; ig_did=D7F46B58-639C-46B1-BF31-779A189F7A45; mid=YEZv-AALAAFz35RVfYZ3X3njIo6Y; fbm_124024574287414=base_domain=.instagram.com; shbid=17682; shbts=1617091529.5876863; csrftoken=MTrR1zOHS71qTpwzncrk8Ow85L5bURfK; ds_user_id=5689845662; sessionid=5689845662%3AV0PWJMItMKwXBD%3A19; rur=ASH; fbsr_124024574287414=FPUwZjsqfe4lUiR-DDRLN_fT4xpy5vFROa0XRYSETck.eyJ1c2VyX2lkIjoiMTAwMDAyNjE2MTc4MDE4IiwiY29kZSI6IkFRRGpfbC1NdEJNTFlfdDJsWnloMXJQN1VaZ2sxbWNWbHdmb3FBa1UzWDlUcmo4ekhzVkg5dmlPZlpPQ0pmN0JRZ2lycDNQX1VhNE4x…cFVrek55VTRMOFExQW9FTnBLZU1qUnZKaFdXUlMwdWRYcThicmNxQmJrakdaQU5Sb0NybjEwY1VfUnZsM1M2WFhpYzhrdFFoLXFXX0RveU5GRUZqUXVGcXhGaXJlVld3S2V3SV9nS2g2cVBYX0hGZm00Zkt4anhaUSIsIm9hdXRoX3Rva2VuIjoiRUFBQnd6TGl4bmpZQkFIQVdhZ3daQ21weVpCVlpBWkNoTlg0c3V0YXZCWkNwcUVMeDR1WkNSeDhOUlpBWkFEOTB2MVhlRjg4ZEo1TUNYSUdGbHFtZzRLNFU3a284alpBQmFsM2FaQWF0NjdMUlhzSVJhRkVqOVNrYU5aQ1RWSE14UVZFa3V1azFzZ0k5NERzU0NaQVdyWkFaQ0k2REpaQ0RTUUJCSlpDRVVzUmtIeFFwUjYyQTFTODJlVGdpUUJzWkIiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTYxNzI5NTI5OX0"
    request_header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "el-GR,el;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Cookie": mozilla_cookies,
        "Host": "www.instagram.com",
        "Referer": "https://www.instagram.com/?hl=el",
        "TE": "Trailers",
        "X-IG-App-ID": "936619743392459",
        "X-IG-WWW-Claim": "hmac.AR2l9mHkjaBgGD3I5V-gBGSH5Kc2uZy07Rav-x0jX-9f5h-j",
        "X-Requested-With": "XMLHttpRequest"
    }


    def start_requests(self):
        for user in self.users_to_scrape:
            print(user)
            profile_url = f"https://www.instagram.com/{user}/?hl=el"

            yield scrapy.Request(profile_url, callback=self.parse, headers=self.request_header)

    def parse(self, response):
        response_script = response.xpath("//script[starts-with(.,'window._sharedData')]/text()").extract_first()
        last_post_date = 0
        #stop_search defines if all the posts of a profile that where uploaded after 1/1/2020 were scraped.If so,then stop_search=True.
        stop_search = False

        if response_script and response_script.__contains__("ProfilePage") :
            script_json = response_script.strip().split('sharedData = ')[1][:-1]
            data = json.loads(script_json)

            user_data = UserData(tagged_users=[], user_posts=[], hashtags=[])
            personal_info = PersonalInfo(followers=0, following=0, posts=0, videos=0, avg_erpost=0, avg_erview=0,
                                            avg_likes=0, avg_comments=0, avg_engagement=0, avg_days_between_posts=0)

            personal_info['user_name'] = data['entry_data']['ProfilePage'][0]['graphql']['user']['username']
            is_private = data['entry_data']['ProfilePage'][0]['graphql']['user']['is_private']
            
            if not is_private:
                personal_info['followers'] = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
                personal_info['following'] = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_follow']['count']
                
                if personal_info['followers'] > self.followers_limit:
                    biography = data['entry_data']['ProfilePage'][0]['graphql']['user']['biography']
                    biography_tags = re.findall('@(.+?)[^0-9a-zA-Z._]', biography)

                    if biography_tags:
                        self.extract_tags_from_list(biography_tags,user_data['tagged_users'], "tags")

                    personal_info['user_id'] = data['entry_data']['ProfilePage'][0]['graphql']['user']['id']

                    account_type = data['entry_data']['ProfilePage'][0]['graphql']['user']['business_category_name']
                    if  account_type and account_type is not None:
                        personal_info['account_type'] = data['entry_data']['ProfilePage'][0]['graphql']['user']['business_category_name']    
                    else:
                        personal_info['account_type'] = "General Purpose"

                    account_category = data['entry_data']['ProfilePage'][0]['graphql']['user']['category_enum']
                    if account_category and account_category is not None:     
                        personal_info['account_category'] = data['entry_data']['ProfilePage'][0]['graphql']['user']['category_enum']
                    else:
                        personal_info['account_category'] = "General Purpose"

                    posts_edges = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']

                    for edge in posts_edges:
                        post_date = int(edge['node']['taken_at_timestamp'])

                        #1577829600 is the timestamp for 1/1/2020
                        if(post_date >= 1577829600) :
                            if edge['node']['__typename'] == "GraphSidecar":
                                post = SlideShow(likes=0, comments=0, er_post=0, er_comments_post=0, slidePosts=[], post_tagged_users=[], post_hashtags=[])
                            else:
                                post = RegularPost(likes=0, comments=0, er_post=0, er_comments_post=0, post_tagged_users=[], post_hashtags=[])

                            personal_info['posts'] += 1
                            post['post_id'] = edge['node']['id']
                            post['post_date_timestamp'] = edge['node']['taken_at_timestamp']
                            post['likes'] = float(edge['node']['edge_liked_by']['count'])
                            post['comments'] = edge['node']['edge_media_to_comment']['count']

                            #er_comments_post = (post_likes + post_comments) / profile_followers
                            post['er_comments_post'] = float((post['likes'] + post['comments'])/personal_info['followers']) * 100

                            #er_post = post_likes / profile_followrers
                            post['er_post'] = post['likes'] / personal_info['followers'] * 100

                            #avg_likes = total_likes / number_of_posts
                            personal_info['avg_likes'] += post['likes']

                            #avg_comments = total_comments / number_of_posts
                            personal_info['avg_comments'] += post['comments']

                            #avg_engagement = total_er_comments_post / number_of_posts
                            personal_info['avg_engagement'] += post['er_comments_post']

                            #avg_erpost = total_er_post / number_of_posts
                            personal_info['avg_erpost'] += post['er_post']

                            if personal_info['posts'] > 1:
                                #avg_days_between_posts: average days between consecutive posts
                                #(60*60*24): conversion of seconds to days
                                personal_info['avg_days_between_posts'] += ((last_post_date - edge['node']['taken_at_timestamp']) / (60*60*24))
                            last_post_date = edge['node']['taken_at_timestamp']

                            if edge['node']['edge_media_to_caption']:
                                post_captions = edge['node']['edge_media_to_caption']
                                captions = ""
                                for i in post_captions['edges']:
                                    captions += i['node']['text'] + "\n"

                                captions_tags = re.findall('@(.+?)[^0-9a-zA-Z._]', captions)   
                                self.extract_tags_from_list(captions_tags, user_data['tagged_users'], "tags")
                                self.extract_tags_from_list(captions_tags, post['post_tagged_users'], "tags")
                                captions_hashtags = re.findall(r"#(\w+)", captions)
                                self.extract_tags_from_list(captions_hashtags, user_data['hashtags'], "hashtags")
                                self.extract_tags_from_list(captions_hashtags, post['post_hashtags'], "hashtags")

                            if edge['node']['edge_media_to_tagged_user']:
                                inpost_tagged_users = edge['node']['edge_media_to_tagged_user']
                                if inpost_tagged_users:
                                    self.extract_tags_from_edges(inpost_tagged_users['edges'], user_data['tagged_users'])
                                    self.extract_tags_from_edges(inpost_tagged_users['edges'], post['post_tagged_users'])
    
                            post_type = edge['node']['__typename']

                            if post_type == "GraphSidecar":
                                post['post_type'] = "slideshow"
                                slides = edge['node']['edge_sidecar_to_children']['edges']

                                slideshow_erview = 0
                                slideshow_videos = 0

                                for slide in slides:
                                    slidepost = SlidePost()
                                    slidepost['slide_id'] = slide['node']['id'] 

                                    if slide['node']['edge_media_to_tagged_user']:
                                        self.extract_tags_from_edges(slide['node']['edge_media_to_tagged_user']['edges'], user_data['tagged_users'])
                                        self.extract_tags_from_edges(slide['node']['edge_media_to_tagged_user']['edges'], post['post_tagged_users'])

                                    if slide['node']['is_video']:
                                        slideshow_videos += 1
                                        personal_info['videos'] += 1
                                        slidepost['slide_type'] = "video"
                                        slidepost['slide_views'] = float(slide['node']['video_view_count'])

                                        #slidepost_erview = slideshow_likes / slide_views
                                        slidepost['er_view'] = 0
                                        if slidepost['slide_views'] != 0:
                                            slidepost['er_view'] = post['likes'] / slidepost['slide_views'] * 100
                                            slideshow_erview += slidepost['er_view']

                                        #avg_erview = total_erview / number_of_videos
                                        personal_info['avg_erview'] += slidepost['er_view']
                                    else:
                                        slidepost['slide_type'] = "Photo"

                                    post['slidePosts'].append(dict(slidepost))

                                #slideshow_erview = total_slidshow_erview / number_of_slideshow_videos
                                if slideshow_videos != 0:
                                    post['slideshow_erview'] = round(float(slideshow_erview / slideshow_videos), 2)

                                user_data['user_posts'].append(dict(post))
                            else:
                                if edge['node']['is_video']:
                                    personal_info['videos'] += 1
                                    post['post_type'] = "video"
                                    post['views'] = float(edge['node']['video_view_count'])

                                    #post_erview = post_likes / post_views
                                    post['er_view'] = 0
                                    if post['views'] != 0:
                                        post['er_view'] = post['likes'] / post['views'] * 100
                                    personal_info['avg_erview'] += post['er_view']
                                else:
                                    post['post_type'] = "photo"
                                
                                user_data['user_posts'].append(dict(post))
                        else:
                            stop_search = True
                            break

                    #Instagram seperates profile posts to groups of 12.next_page_bool defines if the following dozen of posts exists. 
                    next_page_bool = \
                        data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info'][
                            'has_next_page']

                    if next_page_bool and not stop_search:
                        user_data['personal_info'] = personal_info  
                        cursor = \
                            data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info'][
                                'end_cursor']
                        meta_di = {'id': personal_info['user_id'], 'first': 12, 'after': cursor, 'user_data': dict(user_data), 'last_post_date': last_post_date}

                        request_di={'id': personal_info['user_id'], 'first': 12, 'after': cursor, 'username': personal_info['user_name']}
                        params = {'query_hash': 'e769aa130647d2354c40ea6a439bfc08', 'variables': json.dumps(request_di)}
                        url = 'https://www.instagram.com/graphql/query/?' + urlencode(params)

                        yield scrapy.Request(url, callback=self.parse_pages, headers=self.request_header, meta={'meta_di': meta_di})
                    else:
                        print("CRAWLED:" + personal_info['user_name'])

                        if personal_info['posts'] != 0:
                            personal_info['avg_erpost'] = round(float(personal_info['avg_erpost'] / personal_info['posts']), 2)
                            personal_info['avg_likes'] = int(personal_info['avg_likes'] / personal_info['posts'])
                            personal_info['avg_comments'] = int(personal_info['avg_comments'] / personal_info['posts'])
                            personal_info['avg_engagement'] = round(float(personal_info['avg_engagement'] / personal_info['posts']), 2)

                        if personal_info['posts'] > 1:
                            personal_info['avg_days_between_posts'] = int(personal_info['avg_days_between_posts'] / (personal_info['posts'] - 1))

                        if personal_info['videos'] > 0:
                            personal_info['avg_erview'] = round(float(personal_info['avg_erview'] / personal_info['videos']), 2)
                        else:
                            personal_info['avg_erview'] = 0

                        user_data['personal_info'] = personal_info

                        yield dict(user_data)

    def parse_pages(self, response):
        data = json.loads(response.text)
        meta_di = response.meta['meta_di']
        user_data = meta_di['user_data']
        last_post_date = int(meta_di['last_post_date'])

        stop_search = False 
        next_page_bool = data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
        post_edges = data['data']['user']['edge_owner_to_timeline_media']['edges']
        
        for edge in post_edges:
            post_date = int(edge['node']['taken_at_timestamp'])

            if(post_date >= 1577829600):
                if edge['node']['__typename']=="GraphSidecar":
                    post = SlideShow(likes=0, comments=0, er_post=0, er_comments_post=0, slidePosts=[], post_tagged_users=[], post_hashtags=[])
                else:
                    post = RegularPost(likes=0, comments=0, er_post=0, er_comments_post=0, post_tagged_users=[], post_hashtags=[])

                user_data['personal_info']['posts'] += 1
                post['post_id'] = edge['node']['id']
                post['post_date_timestamp'] = edge['node']['taken_at_timestamp']
                post['likes'] = float(edge['node']['edge_media_preview_like']['count']) 
                post['comments'] = float(edge['node']['edge_media_to_comment']['count'])
                post['er_post'] = post['likes'] / float(user_data['personal_info']['followers']) * 100
                post['er_comments_post'] = float((post['likes']+post['comments']) / user_data['personal_info']['followers']) * 100 

                user_data['personal_info']['avg_likes'] += post['likes']
                user_data['personal_info']['avg_comments'] += post['comments']
                user_data['personal_info']['avg_engagement'] += post['er_comments_post']
                user_data['personal_info']['avg_erpost'] += post['er_post']
                user_data['personal_info']['avg_days_between_posts'] += ((last_post_date - edge['node']['taken_at_timestamp']) / (60*60*24))

                last_post_date = edge['node']['taken_at_timestamp']
                
                if edge['node']['edge_media_to_caption']:
                    captions = ""
                    for i in edge['node']['edge_media_to_caption']['edges']:
                        captions += i['node']['text'] + "\n"

                    captions_tags = re.findall('@(.+?)[^0-9a-zA-Z._]', captions)  
                    self.extract_tags_from_list(captions_tags,user_data['tagged_users'], "tags")
                    self.extract_tags_from_list(captions_tags, post['post_tagged_users'], "tags")

                    captions_hashtags = re.findall(r"#(\w+)", captions) 
                    self.extract_tags_from_list(captions_hashtags, user_data['hashtags'], "hashtags")
                    self.extract_tags_from_list(captions_hashtags, post['post_hashtags'], "hashtags")     

                if edge['node']['edge_media_to_tagged_user']:
                    self.extract_tags_from_edges(edge['node']['edge_media_to_tagged_user']['edges'], user_data['tagged_users'])
                    self.extract_tags_from_edges(edge['node']['edge_media_to_tagged_user']['edges'], post['post_tagged_users'])

                post_type = edge['node']['__typename']

                if post_type == "GraphSidecar":
                    post['post_type'] = "slideshow"
                    slides = edge['node']['edge_sidecar_to_children']['edges']

                    slideshow_erview = 0
                    slideshow_videos = 0

                    for slide in slides:
                        slidepost = SlidePost()
                        slidepost['slide_id'] = slide['node']['id']

                        if slide['node']['edge_media_to_tagged_user']:
                            self.extract_tags_from_edges(slide['node']['edge_media_to_tagged_user']['edges'], user_data['tagged_users'])
                            self.extract_tags_from_edges(slide['node']['edge_media_to_tagged_user']['edges'], post['post_tagged_users'])

                        if slide['node']['is_video']:
                            slideshow_videos += 1
                            user_data['personal_info']['videos'] += 1
                            slidepost['slide_type'] = "video"
                            slidepost['slide_views'] = float(slide['node']['video_view_count'])
                            slidepost['er_view'] = 0
                            if slidepost['slide_views'] != 0:
                                slidepost['er_view'] = post['likes'] / slidepost['slide_views'] * 100
                                slideshow_erview += slidepost['er_view']
                            user_data['personal_info']['avg_erview'] += slidepost['er_view']
                        else:
                            slidepost['slide_type'] = "Photo"

                        post['slidePosts'].append(dict(slidepost))

                    if slideshow_videos != 0:
                        post['slideshow_erview'] = round(float(slideshow_erview / slideshow_videos),2)

                    user_data['user_posts'].append(dict(post))
                else:
                    if edge['node']['is_video']:
                        user_data['personal_info']['videos'] += 1
                        post['post_type'] = "video"
                        post['views'] = float(edge['node']['video_view_count'])
                        post['er_view'] = 0
                        if post['views'] != 0:
                            post['er_view'] = post['likes'] / post['views'] * 100
                        user_data['personal_info']['avg_erview'] += post['er_view']
                    else:
                        post['post_type'] = "photo"

                    user_data['user_posts'].append(dict(post))      
            else:
                stop_search = True
                break

        #Updates average values of meta_dict to pass it to the next invoking of the parse_pages method
        meta_di['user_data']['personal_info']['avg_erpost'] = float(user_data['personal_info']['avg_erpost'])
        meta_di['user_data']['personal_info']['avg_erview'] = float(user_data['personal_info']['avg_erview'])
        meta_di['user_data']['personal_info']['videos'] = int(user_data['personal_info']['videos'])
        meta_di['user_data']['personal_info']['avg_likes'] = int(user_data['personal_info']['avg_likes'])
        meta_di['user_data']['personal_info']['avg_comments'] = int(user_data['personal_info']['avg_comments'])
        meta_di['user_data']['personal_info']['avg_engagement'] = float(user_data['personal_info']['avg_engagement'])
        meta_di['last_post_date'] = last_post_date

        if next_page_bool and not stop_search:
            cursor = data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            meta_di['after'] = cursor
            meta_di['user_data']['personal_info']['posts'] = int(user_data['personal_info']['posts'])

            request_di={'id': meta_di['id'], 'first': meta_di['first'], 'after': cursor, 'username': meta_di['user_data']['personal_info']['user_name']}
            params = {'query_hash': 'e769aa130647d2354c40ea6a439bfc08', 'variables': json.dumps(request_di)}
            url = 'https://www.instagram.com/graphql/query/?' + urlencode(params)

            yield scrapy.Request(url, callback=self.parse_pages, headers=self.request_header, meta={'meta_di': meta_di})
        else :
            print("CRAWLED:" + meta_di['user_data']['personal_info']['user_name'])

            if user_data['personal_info']['avg_erpost'] != 0:
                user_data['personal_info']['avg_erpost'] = round(float(user_data['personal_info']['avg_erpost']/user_data['personal_info']['posts']),2)
                user_data['personal_info']['avg_likes'] = int(user_data['personal_info']['avg_likes']/user_data['personal_info']['posts'])
                user_data['personal_info']['avg_comments'] = int(user_data['personal_info']['avg_comments']/user_data['personal_info']['posts'])
                user_data['personal_info']['avg_engagement'] = round(float(user_data['personal_info']['avg_engagement']/user_data['personal_info']['posts']),2)
                user_data['personal_info']['avg_days_between_posts'] = int(user_data['personal_info']['avg_days_between_posts']/(user_data['personal_info']['posts']-1))
            
            if not user_data['personal_info']['videos'] == 0:
                user_data['personal_info']['avg_erview'] = round(float(user_data['personal_info']['avg_erview']/user_data['personal_info']['videos']),2)
            else:
                user_data['personal_info']['avg_erview'] = 0

            yield dict(user_data)


    def extract_tags_from_list(self, extraction_list, insertion_list, type):
        for tag in extraction_list:
            if tag.endswith('.'):
                tag = tag[:-1]
                
            if not tag in insertion_list: 
                insertion_list.append(tag)


    def extract_tags_from_edges(self, extraction_list, insertion_list):
        for edge in extraction_list:
            tag=edge['node']['user']['username']

            if tag.endswith('.'):
                tag = tag[:-1]
                
            if not tag in insertion_list:
                insertion_list.append(tag)

