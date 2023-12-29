import flet
import moviepy.editor as mp
import pandas as pd

from pytube import Search, YouTube, Stream
from flet import Page, Column, Image, TextField, Ref, ListTile, Text, Audio, ProgressBar


def main(page: Page):	
	search_bar = Ref[TextField]()
	results = Ref[Column]()
	loading = Ref[ProgressBar]()

	audio = Audio(src = r'C:\Users\sergi\Documents\repos\flet\assets\Como Un Volcán.mp3')	
	page.overlay.append(audio)

	def download(event):
		loading.current.visible = True
		page.update()
		
		stream = YouTube(event.control.subtitle.value).streams.filter(file_extension = 'mp4').first()
		result = stream.download(output_path = r'assets')


		if not result == '':
			clip = mp.VideoFileClip(result)
			mp3_file = result.replace('.mp4', '.mp3')
			clip.audio.write_audiofile(mp3_file)
			
			loading.current.visible = False

			audio.src = mp3_file
			audio.play()
			audio.autoplay = True

			page.update()

	def search(event):
		if event.control.value:
			search = Search(event.control.value)
			
			if search.results:
				loading.current.visible = True
				results.current.disabled = True
				results.current.controls.clear()

				songs = {
					'Image' : [],
					'Song' : [],
					'Title' : [],
				}

				for result in search.results:
					songs['Image'].append(result.thumbnail_url)
					songs['Song'].append(result.watch_url)
					songs['Title'].append(result.title)

					results.current.controls.append(
						ListTile(leading = Image(src = result.thumbnail_url, width = 120, height = 120), 
			   					title = Text(result.title, size=20,weight='bold'),
								subtitle = Text(result.watch_url, visible = False), on_click = download))
					page.update()

				pd.DataFrame(songs).to_csv(r'C:\Users\sergi\Documents\repos\flet\course\playlist_player\assets\music.csv', index=False)

				loading.current.visible = False	
				results.current.disabled = False
				page.update()


	page.add(TextField(ref = search_bar, label = 'Enter a video name', on_submit = search, autofocus = True),
			 ProgressBar(ref = loading, color = 'red', visible = False),
		  	 Column(ref = results, scroll = flet.ScrollMode.ALWAYS, spacing = 16, height = page.height - 128))


flet.app(target = main, assets_dir = r'assets')