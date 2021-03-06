from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from functools import partial

app = App.get_running_app()


class SpeakerDetails(Factory.ScrollGrid):

    speaker = ObjectProperty(None)

    Builder.load_string('''
<SpeakerDetails>
    AsyncImage:
        source: root.speaker['photo'] 
        opacity: 1 if root.speaker['photo']  else 0
        allow_stretch: True
        size_hint_y: None
        height: dp(200)
        mipmap: True
    BackLabel
        backcolor: app.base_inactive_color[:3] + [.5]
        text: root.speaker['name']
    BackLabel
        text: root.speaker['info']
        ''')

class ScreenTalks(Screen):
    '''
    Screen to display the talk schedule as per talks.json generated by
    pydelhiconf.network every time the app is started. A default
    talk schedule is provided.

    Screen looks like:

    -----------------------------------------
   |              ------------               |
   |              |          |               |
   |              |          |               |
   |              |          |               |
   |              |          |               |
   |              |          |               |
   |              ------------               |
   |              Speaker name               |
   |                                         |
   |About talk                               |
   |                                         |
   |About speaker                            |
   |Social links                             |
   |                                         | 
    -----------------------------------------

    '''

    talkid = StringProperty('')

    Builder.load_string('''
<ScreenTalks>
    spacing: dp(9)
    name: 'ScreenTalks'
    ScrollView
        id: scroll
        ScrollGrid
            id: container
            BackLabel:
                backcolor: app.base_inactive_color[:3] + [.5]
                id: talk_title
            BackLabel:
                id: talk_desc
        ''')
    def on_pre_enter(self):
        container = self.ids.container
        container.opacity = 0

    def on_enter(self, onsuccess=False):
        container = self.ids.container
        
        if self.from_back:
            return

        if len(container.children) > 2:
                container.remove_widget(container.children[0])
        from network import get_data
        talks = get_data('tracks', onsuccess=onsuccess)
        gl = None
        if not talks:
            return
        talk_info = talks['0.0.1'][0][self.talkid]

        self.ids.talk_title.text = talk_info['title']
        self.ids.talk_desc.text = talk_info['description']
        if 'speaker' in talk_info.keys():
            speaker=talk_info['speaker']
            if speaker['name']:
                speaker_details = SpeakerDetails(speaker=speaker)
                if 'social' in speaker:
                    speaker_social = speaker['social'][0]
                    social_len = len(speaker_social)
                    gl = GridLayout(cols=social_len,
                                size_hint_y=None,
                                padding='2dp',
                                spacing='2dp')
                    import webbrowser
                    for social_acc, social_link in speaker_social.items():
                        imbt = Factory.ImBut()
                        imbt.source = 'atlas://data/default/' + social_acc.lower()
                        imbt.on_released = partial(webbrowser.open,social_link)
                        gl.add_widget(imbt)
                    speaker_details.add_widget(gl)
                self.ids.container.add_widget(speaker_details)
        Factory.Animation(opacity=1, d=.3).start(container)
        self.ids.scroll.scroll_y = 1
