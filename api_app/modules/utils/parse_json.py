class ParseJson:
    
    def return_int_for_true( parsed_value, int_to_return=0):

        if isinstance(parsed_value, bool):
            return int_to_return if parsed_value else 0 # return int for True, 0 for False
        elif isinstance(parsed_value, int):
            return int_to_return if parsed_value == int_to_return else 0
        else:
            return 0