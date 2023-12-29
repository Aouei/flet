import flet

from flet import Page, ElevatedButton, Text, Row


def main(page : Page):

    txt_a : Text = Text('A')
    txt_b : Text = Text('B')

    def receive_A(topic : str, message : str):
        txt_a.value = f'Message {message} on topic {topic}' 
        page.update()

    def receive_B(topic : str, message : str):
        txt_b.value = f'Message {message} on topic {topic}'
        page.update()

    def send_A(event):
        page.pubsub.send_all_on_topic('A', 'Hey A')
        page.update()

    def send_B(event):
        page.pubsub.send_all_on_topic('B', 'Hey B')
        page.update()

    page.pubsub.subscribe_topic('A', receive_A)
    page.pubsub.subscribe_topic('B', receive_B)

    page.add(
        Row([ElevatedButton('Send A', on_click = send_A), ElevatedButton('Send B', on_click = send_B)]),
        Row([txt_a, txt_b]),
        )
    

flet.app(target = main)