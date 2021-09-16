# Incoming messages on the server have two parts: TO MESSAGE
# The TO part is an integer specifying the target.
# The MESSAGE part is the actual message and consists
# of TYPE and CONTENT, however we can ignore this split
# as the server only needs to know the TO id to forward
# the complete MESSAGE part to that client.


class Message:

    def __init__(self, raw_message = None):
        if raw_message:
            self.parse(raw_message)
        else:
            self.clear()

    def clear(self):
        self.valid = False
        self.target_id = -1
        self.content = ''

    def parse(self, raw_message):
        self.clear()

        parts = raw_message.split(' ', 1)
        if not len(parts) == 2:
            return

        try:
            self.target_id = int(parts[0])
        except ValueError:
            return

        self.content = parts[1]
        self.valid = True
