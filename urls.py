from django.conf.urls.defaults import *
from movies.views import *
from member.views import *
from club.views import *
from event.views import *
from admin.views import *
from sns.views import *
from apps.views import *
from api.views import *
from django.views.generic.simple import direct_to_template
from django.contrib import admin
from django.http import HttpResponse
import os.path
stylesheet = os.path.join(
    os.path.dirname(__file__), 'stylesheet'
)
script = os.path.join(
    os.path.dirname(__file__), 'script'
)
images = os.path.join(
    os.path.dirname(__file__), 'images'
)
cache = os.path.join(
    os.path.dirname(__file__), 'cache'
)
#files = os.path.join(
#    os.path.dirname(__file__), 'files'
#)
files = '/data/inthemovie/files'

urlpatterns = patterns('',
    (r'^image_proxy/$',image_proxy),
    (r'^link_proxy/$',link_proxy),
    (r'^$',index),
    (r'^err/$', err),
    (r'^tos/$', main_tos),
    (r'^private/$', main_private),
    (r'^notice/$',notice_loading),
    (r'^search/$',movie_search),
    (r'^google6a507a904d8f981a.html$',google_verify),
    (r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nAllow: /", mimetype="text/plain")),

    #oauth url
    (r'^oauth$', oauth),
    (r'^oauth_access/$', oauth_access),
    (r'^sns_profile/$',get_sns_data),
    (r'^sns_logout/$',sns_logout),
    (r'^sns_post/$',sns_post),
    
    (r'^poster$',poster),

    #admin url
    (r'^inthe-movie/admin/$',admin_main),
    (r'^inthe-movie/admin/member/$',member_manage),
    (r'^inthe-movie/admin/member/block/$',member_manage_panalty),
    (r'^inthe-movie/admin/member/block/(\d+)/$',panalty_delete),
    (r'^inthe-movie/admin/member/view/$',member_manage_view),
    (r'^inthe-movie/admin/event/$',event_manage),
    (r'^inthe-movie/admin/event/view/(\d+)/$',event_manage_view),
    (r'^inthe-movie/admin/event/edit/(\d+)/$',event_manage_edit),
    (r'^inthe-movie/admin/event/delete/(\d+)/$',event_manage_delete),
    (r'^inthe-movie/admin/event/copy/(\d+)/$',event_manage_copy),
    (r'^inthe-movie/admin/event/create/$', event_create),
    (r'^inthe-movie/admin/hotmovie/$', hotmovie_manage),
    (r'^inthe-movie/admin/hotmovie/select$', hotmovie_select),
    (r'^inthe-movie/admin/club/$',club_manage),
    (r'^inthe-movie/admin/club/create/$', club_create),
    (r'^inthe-movie/admin/email/$', email_manage),    
    (r'^inthe-movie/admin/email/view$', email_manage_view),    
    (r'^inthe-movie/admin/ad/$', banner),    
    (r'^inthe-movie/admin/ad/edit/(\d+)/$',banner_edit),
    (r'^inthe-movie/admin/ad/delete/(\d+)/$',banner_delete),

    (r'^inthe-movie/admin/panalty/(\d+)/$',memeber_panalty),
    # member urls
    (r'^login/$', login),
    (r'^logout/$', logout),
    (r'^join/$', join),
    (r'^join/success/$', join_success),
    (r'^join/auth$', join_auth),
    (r'^join/validate$', join_validate),
    (r'^find/$', member_find),
    # mypage
    (r'^user/(\w+)/$',mypage_point),
    (r'^user/(\w+)/point/$',mypage_point),
    
    (r'^user/(\w+)/message/$',mypage_message),
    (r'^user/(\w+)/message/post/$',mypage_message_post), 
    (r'^user/(\w+)/message/read/(\d+)/$', mypage_message_read),
    (r'^user/(\w+)/message/delete/(\d+)/$', mypage_message_delete),
    (r'^user/(\w+)/info/$',mypage_info),
    (r'^user/(\w+)/dropout/$',member_dropout),

    (r'^banner/$',get_banner),
    # club
    (r'^club/$', club_main),
    (r'^club/(\w+)/$',club_list),
    (r'^club/(\w+)/page/(\d+)/$',club_list),
    (r'^club/(\w+)/post/$',club_post),
    (r'^club/(\w+)/post/(\d+)/$',club_post_view),
    (r'^club/(\w+)/edit/(\d+)/$',club_post_edit),
    (r'^club/(\w+)/delete/(\d+)/$',club_post_delete),
    (r'^club/comment/(\w+)/(\d+)/$',club_comment_list),
    (r'^club/comment/request$',club_comment_post),
    (r'^club/comment/delete/(\w+)/(\d+)/$',club_comment_delete),
    (r'^club/comment/edit/(\w+)/(\d+)/$',club_comment_edit),
    (r'^image_upload/(\w+)/$',image_upload),
    (r'^club/push/(\d+)/$', blog_push),
    
    # gnb mains
    (r'^movies/$', movies_main),
    
    (r'^events/$', events_main),
    (r'^events/(\w+)/$', events_main),
    (r'^events/view/(\d+)/$',events_view),
    (r'^events/request$', events_request),
    (r'^events/request/get$', get_events_request),
    (r'^events/delete$', events_delete),
    
    (r'^stylesheet/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': stylesheet} ),
    (r'^script/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': script} ),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': images} ),
    (r'^files/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': files} ),
    (r'^cache/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': cache} ),

    (r'^(\w+)/$',hotmovie_main),
    (r'^(\w+)/blog/$',hotmovie_blog),
    (r'^(\w+)/blog/page/(\d+)/$',hotmovie_blog),
    (r'^(\w+)/news/$',hotmovie_news),
    (r'^(\w+)/news/page/(\d+)/$',hotmovie_news),
    (r'^(\w+)/video/$',hotmovie_video),
    (r'^(\w+)/video/page/(\d+)/$',hotmovie_video),
    (r'^(\w+)/photo/$',hotmovie_photo),
    (r'^(\w+)/photo/page/(\d+)/$',hotmovie_photo),
    (r'^(\w+)/review/$',hotmovie_review),
    (r'^(\w+)/vlaah/$',hotmovie_vlaah),
    (r'^(\w+)/sns/(\w+)/$',hotmovie_sns),

    (r'^apps/hotmovies$', app_hotmovies),
    (r'^apps/events$', app_events),
    (r'^apps/events/(\w+)/$', app_events),
    (r'^apps/resize/$', resize_remote_image),

    (r'^api/event/list$', api_event_list),
    (r'^api/event/(\d+)/$', api_event_view),
    (r'^api/event/request$', api_event_request),
)
