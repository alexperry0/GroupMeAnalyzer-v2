class Member:
    def __init__(self, member_id, name, messages):
        self.member_id = member_id
        self.name = name
        self.messages = messages

    def likes_received(self):
        likes_received = 0
        for message in self.messages:
            likes_received += len(message['favorited_by'])

        return likes_received

    def messages_sent(self):
        return len(self.messages)

    def words_sent(self):
        words_sent = 0
        for message in self.messages:
            text = message['text'] or ''
            for char in '-.,\n':
                text = text.replace(char, ' ')
            words_sent = len(text.split())

        return words_sent


