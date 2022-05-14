class SpecialCharacterMap(object):

    def __init__(self, json_string):
        self.json_string = json_string
        self.special_character_map = dict()
        self.double_string_special_character_location = []

        self.single_string_special_characters = {'\n', '"', "'", ":", "{", '}', ","}
        self.double_string_special_characters = {'//', '/*', '*/'}
        self.double_string_special_characters_components = set(
            ''.join(self.double_string_special_characters))

    def add_double_string_special_character_map(self):
        for location in range(len(self.double_string_special_character_location)):
            try:
                first_string = self.double_string_special_character_location[location][0]
                first_string_location = self.double_string_special_character_location[location][1]
                next_string = self.double_string_special_character_location[location + 1][0]
                next_string_location = self.double_string_special_character_location[location + 1][1]

                if first_string + next_string in self.double_string_special_characters:
                    if first_string_location + 1 == next_string_location:
                        key = first_string_location
                        value = first_string + next_string
                        self.special_character_map[key] = value
            except:
                continue

    def make(self):
        for string, location in zip(self.json_string, range(len(self.json_string))):
            if string in self.double_string_special_characters_components:
                self.double_string_special_character_location.append((string, location))
            elif string in self.single_string_special_characters:
                self.special_character_map[location] = string
        self.add_double_string_special_character_map()
        return self.special_character_map


class CommentedJsonParser(object):

    def __init__(self, json_string):
        self.raw_json_string = json_string

        self.new_json_parts = []
        self.recent_comment_start_location = None
        self.recent_comment_end_location = None
        self.recent_json_structure_start_location = None
        self.recent_json_character = None
        self.ignoring_characters = False
        self.recent_ignore_character = None

        self.cursor = 0

        self.special_character_complement = {
            '/*': {'*/'}
            , '//': {'\n', ':', ','}
            , '"': {'"'}
            , "'": {"'"}
            , '{': {':'}
            , ':': {'}', ','}
            , ',': {'{'}
        }
        self.quote_characters = {"'", '"'}
        self.comment_start_characters = {'//', '/*'}
        self.ignoring_until_end_characters = {'//', '/*', '"', "'"}
        self.json_structure_character = {'{', '}', ':', ','}
        self.all_special_characters = {'//', '/*', '*/', '"', "'", '{', '}', ':', ',', '\n', '/', '*'}

    def parse(self):
        special_character_map = SpecialCharacterMap(self.raw_json_string).make()
        ordered_special_character_location = list(special_character_map.keys())
        ordered_special_character_location.sort()

        for i in range(len(ordered_special_character_location)):
            string_location = ordered_special_character_location[i]
            special_character = special_character_map[string_location]

            if self.ignoring_characters:
                if special_character in self.special_character_complement[self.recent_ignore_character]:
                    if special_character in self.quote_characters:
                        self.new_json_parts.append(self.raw_json_string[self.cursor:string_location + 1])
                    elif special_character == ':':
                        self.recent_json_character = special_character
                        self.recent_json_structure_start_location = string_location
                        self.new_json_parts.append(f'"key_{i}":')
                    self.ignoring_characters = False
                    self.cursor = string_location + len(special_character)
                else:
                    continue
            elif special_character in self.ignoring_until_end_characters:
                self.new_json_parts.append(self.raw_json_string[self.cursor:string_location])
                self.recent_ignore_character = special_character
                self.ignoring_characters = True
                self.cursor = string_location
                if special_character in self.comment_start_characters:
                    self.recent_comment_start_location = string_location
            elif special_character in self.json_structure_character:
                if self.recent_json_character:
                    if special_character != self.special_character_complement[self.recent_json_character]:
                        if special_character == self.recent_json_character == ':':
                            self.new_json_parts.insert(-1, ',')
                            self.recent_json_character = ','
                        else:
                            self.recent_json_character = special_character
                else:
                    self.new_json_parts.append(self.raw_json_string[self.cursor:string_location + 1])
                    self.recent_json_character = special_character
                    self.cursor = string_location + 1
                self.recent_json_structure_start_location = string_location

        if not self.ignoring_characters:
            self.new_json_parts.append(self.raw_json_string[self.cursor:len(self.raw_json_string)])
        self.new_json_parts = [strings.strip(' ') for strings in self.new_json_parts]
        new_json_string = ''.join(self.new_json_parts)
        new_json_string = new_json_string.replace(': ', ':')
        return new_json_string
