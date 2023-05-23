"""
This is an Alexa lambda function implementaion of the popular game Noughts and Crosses,
otherwise known as Tic Tac Toe.

Copyright: Infiniconcept, 2017
Contact: info@infiniconcept.com

Intent schema:
{"intents": [
    {
      "intent": "SelectDifficulty",
      "slots": [
        {
          "name": "Difficulty",
          "type": "LIST_OF_DIFFICULTIES"
        }
      ]
    },
    {
      "intent": "PlayerMove",
      "slots": [
        {
          "name": "Move",
          "type": "LIST_OF_MOVES"
        }
      ]
    },
    {
      "intent": "CheckSquare",
      "slots": [
        {
          "name": "Square",
          "type": "LIST_OF_MOVES"
        }
      ]
    },
    {
      "intent": "CheckBoard",
      "slots": []
    },
    {"intent": "AMAZON.StartOverIntent"},
    {"intent": "AMAZON.HelpIntent"},
    {"intent": "AMAZON.YesIntent"},
    {"intent": "AMAZON.NoIntent"},
    {"intent": "AMAZON.CancelIntent"},
    {"intent": "AMAZON.StopIntent"}
  ]
}

LIST_OF_MOVES slot values:
A1
A2
A3
B1
B2
B3
C1
C2
C3

LIST_OF_DIFFICULTIES slot values:
easy
medium
hard

Sample utterances:
SelectDifficulty {Difficulty}
SelectDifficulty Make it {Difficulty}
SelectDifficulty I want {Difficulty}
SelectDifficulty Let's play {Difficulty}
SelectDifficulty {Difficulty} please

PlayerMove {Move}
PlayerMove {Move} please
PlayerMove My move is {Move}
PlayerMove Mark {Move}

CheckSquare Check {Square}
CheckSquare Check square {Square}
CheckSquare Check position {Square}
CheckSquare What is on {Square}
CheckSquare Tell me what is on {Square}

CheckBoard How does the board look like
CheckBoard What is on the board
CheckBoard Tell me what is on the board
CheckBoard Tell me all positions
CheckBoard What is on all squares
CheckBoard What is on all fields
CheckBoard What is in all positions
CheckBoard Tell me what is on all squares
CheckBoard Check board

AMAZON.StartOverIntent new game
AMAZON.StartOverIntent restart
AMAZON.StartOverIntent start a new game

AMAZON.HelpIntent help
AMAZON.HelpIntent instructions
AMAZON.HelpIntent help me
AMAZON.HelpIntent what can I do
AMAZON.HelpIntent how do I play

AMAZON.YesIntent sure
AMAZON.YesIntent why not
AMAZON.YesIntent go ahead
"""

from __future__ import print_function
from random import randint
from random import choice
import copy
import re

# states
STATE_SELECTING_DIFFICULTY = 1
STATE_SELECTING_FIRST = 2
STATE_PLAYING = 3
STATE_FINISHED = 4

# --------------- Helpers that build all the responses ----------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session, cardOutput=""):
    # remove SSML tags for card output
    if not cardOutput:
        ca = re.sub('<[^<]+>', "", output)
    else:
        ca = cardOutput

    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" + output + "</speak>"
#            'type': 'PlainText',
#            'text': output 
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': ca
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def build_session_attributes(attributes):
    # final update/reformat of sesssion attributes, if required
    # nothing to do at the moment
    return attributes

def welcome_response(attributes):
    card_title = "Welcome to Noughts and Crosses"
    attributes["lastOutput"] = "Please select difficulty: easy, medium or hard. "
    attributes["lastRepeat"] = "Please select difficulty: easy, medium or hard. "
    speech_output = "Welcome to Noughts and Crosses! " + attributes["lastOutput"]
    reprompt_text = attributes["lastRepeat"] 
    should_end_session = False
    session_attributes = build_session_attributes(attributes)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def select_difficulty_response(attributes):
    card_title = "Select difficulty"
    attributes["lastOutput"] = "Please select difficulty: easy, medium or hard. "
    attributes["lastRepeat"] = "Please select difficulty: easy, medium or hard. "
    speech_output = attributes["lastOutput"]
    reprompt_text = attributes["lastRepeat"] 
    should_end_session = False
    session_attributes = build_session_attributes(attributes)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    responses = ["OK then... Goodbye for now!  ", 
        "Bye bye, come back soon! ",
        "I will be a bit sad while you are gone, so come back soon. Goodbye! ",
        "Thank you and talk to you later! "]

    card_title = "Goodbye"
    speech_output = select_random_response(responses)
    should_end_session = True
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def handle_help_request(attributes):
    card_title = "Help"
    speech_output = "Noughts and crosses is a game played on a 3 by 3 square board, on which two players place noughts and crosses in turns. " \
                    "Whoever first places 3 of the same marks in a line, wins. Rows are marked: A, B and C, and columns: 1, 2 and 3. "\
                    "During your turn, you say in which square you want to place your mark, for example A2 or C3. \n\n"\
                    "You can also ask to check what is already in a given square by saying check square, "\
                    "check what\'s on the entire board by saying check board, restart the game or quit. " \
                    "<break time=\"1.5s\"/> \n\n" + attributes["lastRepeat"]
    reprompt_text = attributes["lastRepeat"]
    should_end_session = False
    session_attributes = build_session_attributes(attributes)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_unsolicited_yes(attributes):
    card_title = "Not sure what you want me to do"
    speech_output = "I am glad you agree with me, but not sure what you want me to do. \n\n" + attributes["lastOutput"]
    reprompt_text = attributes["lastRepeat"]
    should_end_session = False
    session_attributes = build_session_attributes(attributes)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_unsolicited_no(attributes):
    card_title = "Not sure what you want me to do"
    speech_output = "I am not sure why you said no. \n\n" + attributes["lastOutput"]
    reprompt_text = attributes["lastRepeat"]
    should_end_session = False
    session_attributes = build_session_attributes(attributes)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_not_understood(attributes):
    card_title = "Not sure what you want me to do"
    speech_output = "I am sorry but I did not understand what you wanted me to do. \n\n" + attributes["lastOutput"]
    reprompt_text = attributes["lastRepeat"]
    should_end_session = False
    session_attributes = build_session_attributes(attributes)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_wrong_state(attributes):
    #card_title = "Wrong state"
    #speech_output = "Command sent in wrong state: " + str(attributes["state"]) + " . " + attributes["lastRepeat"]
    card_title = "Sorry I cannot do it now"
    speech_output = "Sorry I cannot do that right now. \n\n" + attributes["lastRepeat"]
    reprompt_text = attributes["lastRepeat"]
    should_end_session = False
    session_attributes = build_session_attributes(attributes)
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# this function should be used for all regular messages as it remembers what's been said, allowing the user to interrupt the game with other questions
def say_message(cardName, message, repeat, attributes, cardMessage, changeLast = True):
    if changeLast:
        attributes["lastOutput"] = message
        attributes["lastRepeat"] = repeat
    speech_output = message
    reprompt_text = repeat
    should_end_session = False
    session_attributes = build_session_attributes(attributes)
    return build_response(session_attributes, build_speechlet_response(cardName, speech_output, reprompt_text, should_end_session, cardMessage))

def select_random_response(responses):
    return responses[randint(0,len(responses) - 1)]
   
# ----------------------- Events
# ---------------------------------------------------
def on_session_started(session_started_request, session):
    """ Called when the session starts """
    #print("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they want """
    #print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])

    # Create/reset attributs - they should not exist yet, but check just in case
    if 'attributes' not in session:
        attributes = {}
        # set the initial state and game context values
        session['attributes'] = attributes
    else:
        attributes = session['attributes']

    initialise_attributes(attributes)
    return welcome_response(attributes)

# if the skill gets into the wrong state, set a meaningful re-prompt
def set_wrong_state_reprompt(state):
    if state == STATE_SELECTING_DIFFICULTY:
        msg = "Please select difficulty: easy, medium or hard. "
    elif state == STATE_SELECTING_FIRST:
        msg = "Who should go first, do you want to make the first move? Say yes or no. "
    elif state == STATE_PLAYING:
        msg = "What is your move? Say row followed by column, for example A1. "
    else:
        msg = "Try to say something else"
    return msg

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    #print("on_intent: session: " + str(session))
    #print("           intent_request: " + str(intent_request))
    #print("on_intent: intent: " + intent_request['intent']['name'])

    # get attributes (i.e. game state)
    if 'attributes' not in session or not session['attributes']:
        # if attributes not in session then initialise them (e.g. user launched intent straight away)
        attributes = {}
        initialise_attributes(attributes)
        session['attributes'] = attributes
    else:
        attributes = session['attributes']

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # "select difficulty" intent 
    if intent_name == "SelectDifficulty":
        if attributes['state'] == STATE_SELECTING_DIFFICULTY:

            valid = False
            difficulty = ""
            if 'Difficulty' in intent['slots'].keys() and 'value' in intent['slots']['Difficulty'].keys():
                difficulty = intent['slots']['Difficulty']['value'].lower()
                if difficulty in ["easy", "medium", "hard"]:
                    valid = True

            if not valid:
                if not difficulty:
                    difficulty = "This"
                msg = difficulty + " is not a valid difficulty level. " \
                    "Please select difficulty: easy, medium or hard."
                return say_message("Invalid difficulty level",
                    msg,
                    "Please select difficulty: easy, medium or hard. ",
                    attributes,
                    msg)

            # update attributes with the choice
            attributes["difficulty"] = difficulty

            attributes['state'] = STATE_SELECTING_FIRST

            return say_message("Who goes first?",
                "Difficulty set to " + attributes["difficulty"] + ". Do you want to make the first move?",
                "Who should go first, do you want to make the first move? Say yes or no. ",
                attributes,
                "")
        else:
            if not attributes["lastRepeat"]:
                attributes["lastRepeat"]=set_wrong_state_reprompt(attributes['state'])
            return handle_wrong_state(attributes);

    # "player move" intent with the main game logic
    elif intent_name == "PlayerMove":
        if attributes['state'] == STATE_PLAYING:

            # get player's move
            valid = False
            move = ""
            if 'Move' in intent['slots'].keys() and 'value' in intent['slots']['Move'].keys():
                move = intent['slots']['Move']['value'].upper()
                if move in ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]:
                    valid = True

            if not valid:
                if not move:
                    move = "Nothing"
                return say_message("Invalid move",
                    move + " is not a valid square. " \
                    "Please select another square. What is your move?",
                    "What is your move? Say row followed by column, for example A1. ",
                    attributes,
                    "Please select another square. What is your move? \n\n" + \
                    drawBoard(attributes["board"]))

            playerMove = convertFieldToBoardNumber(move);

            # check if spate already occupied
            if not isSpaceFree(attributes["board"], playerMove):
                return say_message("Your move",
                    convertBoardNumberToField(playerMove) + " is already occupied by a " + convertLetterToWord(attributes["board"][playerMove]) + ". " \
                    "Please select another square. What is your move?",
                    "What is your move? Say row followed by column, for example A1. ",
                    attributes,
                    convertBoardNumberToField(playerMove) + " is already occupied by a " + convertLetterToWord(attributes["board"][playerMove]) + ". " + \
                    "Please select another square. What is your move? \n\n" + \
                    drawBoard(attributes["board"]))

            # update the board with player's move
            makeMove(attributes["board"], attributes["player"], playerMove)

            # check if player won
            if isWinner(attributes["board"], attributes["player"]):
                attributes["state"] = STATE_FINISHED
                return say_message("You win!",
                    "Congratulations, you win! <break time=\"1s\"/>Do you want to play again? ",
                    "Do you want to play again? ",
                    attributes,
                    "Congratulations, you win! Do you want to play again? \n\n" + \
                    drawBoard(attributes["board"]))
            elif isBoardFull(attributes["board"]):
                attributes["state"] = STATE_FINISHED
                return say_message("It's a draw!",
                    "It's a draw, nobody one! <break time=\"1s\"/>Do you want to play again? ",
                    "Do you want to play again? ",
                    attributes,
                    "It's a draw, nobody one! Do you want to play again? \n\n" + \
                    drawBoard(attributes["board"]))

            # get computer's move
            computerMove = getAlexaMove(attributes);

            # update the board with computer's move
            makeMove(attributes["board"], attributes["computer"], computerMove)

            # check if computer won
            if isWinner(attributes["board"], attributes["computer"]):
                attributes["state"] = STATE_FINISHED
                return say_message("You lose!",
                    "I win, you lose! Thank you for the good game. <break time=\"1s\"/>Do you want to play again? ",
                    "Do you want to play again? ",
                    attributes,
                    "I win, you lose! Thank you for the good game. Do you want to play again? \n\n" + \
                    drawBoard(attributes["board"]))
            elif isBoardFull(attributes["board"]):
                attributes["state"] = STATE_FINISHED
                return say_message("It's a draw!",
                    "It's a draw, nobody one! <break time=\"1s\"/>Do you want to play again? ",
                    "Do you want to play again? ",
                    attributes,
                    "It's a draw, nobody one! Do you want to play again? \n\n" + \
                    drawBoard(attributes["board"]))

            # game not finished yet - prompt next move
            return say_message("Your move",
                "You place a " + convertLetterToWord(attributes["player"]) + " in " + convertBoardNumberToField(playerMove) + ". " \
                "I place a " + convertLetterToWord(attributes["computer"]) + " in " + convertBoardNumberToField(computerMove) + ". " \
                "What is your next move?",
                "What is your move? Say row followed by column, for example A1. ",
                attributes,
                "You place a " + convertLetterToWord(attributes["player"]) + " in " + convertBoardNumberToField(playerMove) + ". " \
                "I place a " + convertLetterToWord(attributes["computer"]) + " in " + convertBoardNumberToField(computerMove) + ". " + \
                "What is your next move? \n\n" + \
                drawBoard(attributes["board"]))
        else:
            if not attributes["lastRepeat"]:
                attributes["lastRepeat"]=set_wrong_state_reprompt(attributes['state'])
            return handle_wrong_state(attributes);

    # check square intent
    elif intent_name == "CheckSquare":
        if attributes['state'] == STATE_PLAYING:
            # get player's move
            valid = False
            move = ""
            if 'Square' in intent['slots'].keys() and 'value' in intent['slots']['Square'].keys():
                move = intent['slots']['Square']['value'].upper()
                if move in ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]:
                    valid = True

            if not valid:
                if not move:
                    move = "Nothing"
                return say_message("Invalid square",
                    move + " is not a valid square to check. <break time=\"0.7s\"/> \n\n" \
                    + attributes["lastRepeat"],
                    attributes["lastRepeat"],
                    attributes,
                    move + " is not a valid square to check. \n" \
                    + attributes["lastRepeat"] + "\n\n" + \
                    drawBoard(attributes["board"]),
                    False)
            else:
                content = convertLetterToWord(getSpaceContent(attributes["board"], convertFieldToBoardNumber(move)))
                if content in ["cross","nought"]:
                    content = "a " + content
                return say_message("Square Content",
                    move + " is " + content + ". <break time=\"0.7s\"/> \n\n" \
                    + attributes["lastRepeat"],
                    attributes["lastRepeat"],
                    attributes,
                    move + " is " + content + ".\n" + \
                    attributes["lastRepeat"] + "\n\n" + \
                    drawBoard(attributes["board"]),
                    False)
        else:
            if not attributes["lastRepeat"]:
                attributes["lastRepeat"]=set_wrong_state_reprompt(attributes['state'])            
            return handle_wrong_state(attributes);

    # check board intent
    elif intent_name == "CheckBoard":
        if attributes['state'] == STATE_PLAYING:
            content = sayBoard(attributes["board"])
            return say_message("Board Content",
                content + ". <break time=\"1.0s\"/> " \
                + attributes["lastRepeat"],
                attributes["lastRepeat"],
                attributes,
                drawBoard(attributes["board"]) + "\n\n" + attributes["lastRepeat"],
                False)
        else:
            if not attributes["lastRepeat"]:
                attributes["lastRepeat"]=set_wrong_state_reprompt(attributes['state'])
            return handle_wrong_state(attributes);

    # "yes" intent
    elif intent_name == "AMAZON.YesIntent":
        if attributes['state'] == STATE_SELECTING_FIRST:
            attributes['state'] = STATE_PLAYING
            # new game - clear board
            clearBoard(attributes)
            return say_message("Your move",
                "You start. What is your first move?",
                "What is your move? Say row followed by column, for example A1. ",
                attributes,
                "You start. What is your first move? \n\n" + \
                drawBoard(attributes["board"]))
        elif attributes['state'] == STATE_FINISHED:
            attributes['state'] = STATE_SELECTING_DIFFICULTY
            # new game - clear board
            clearBoard(attributes)
            return select_difficulty_response(attributes)
        else:
            return handle_unsolicited_yes(attributes)

    # "no" intent
    elif intent_name == "AMAZON.NoIntent":
        if attributes['state'] == STATE_SELECTING_FIRST:
            attributes['state'] = STATE_PLAYING

            # new game - clear board
            clearBoard(attributes)

            # get computer's move
            computerMove = getAlexaMove(attributes);

            # update the board with computer's move
            makeMove(attributes["board"], attributes["computer"], computerMove)

            return say_message("Your move",
                "I start and place a " + convertLetterToWord(attributes["computer"]) + " in " + convertBoardNumberToField(computerMove) + ". " \
                "What is your move?",
                "What is your move? Say row followed by column, for example A1. ",
                attributes,
                "I start and place a " + convertLetterToWord(attributes["computer"]) + " in " + convertBoardNumberToField(computerMove) + ". " \
                "What is your move? \n\n" + \
                drawBoard(attributes["board"]))
        elif attributes['state'] == STATE_FINISHED:
            return handle_session_end_request()
        else:
            return handle_unsolicited_no(attributes)

    elif intent_name == "AMAZON.HelpIntent":
        return handle_help_request(attributes)

    elif intent_name == "AMAZON.StartOverIntent" or intent_name == "AMAZON.RepeatIntent":
        initialise_attributes(attributes)
        return welcome_response(attributes)

    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()

    else:
        return handle_not_understood(attributes)
#        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    #print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])
    # add cleanup logic here

def initialise_attributes(attributes):
    attributes["state"] = STATE_SELECTING_DIFFICULTY
    attributes["player"] = 'X'
    attributes["computer"] = 'O'
    attributes["difficulty"] = "medium"
    attributes["board"] = [' '] * 10
    attributes["lastOutput"] = ""
    attributes["lastRepeat"] = ""

# --------------------------------- Main handler --------------------------------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
#    print("event.session.application.applicationId=" +
#    event['session']['application']['applicationId'])

    # prevent someone else from configuring a skill that sends requests to this function.
    if (event['session']['application']['applicationId'] != "amzn1.ask.skill.5ea6aaa7-f380-460b-9dc5-5d6c21c1a9a1"):
         raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])                         


#---------------------------------------------------------------------------------------
# -------------------------------- Core procedures -------------------------------------
#---------------------------------------------------------------------------------------

def drawBoard(board):
    # This function prints out the board that it was passed.
    b = []
    for i in range(9):
        if (board[i+1] == " "):
            b.append('~')
        else:
            b.append(board[i+1])

    boardPic = ""
    for i in range(3):
        boardPic += (b[(i*3)]+b[(i*3)+1]+b[(i*3)+2]) + "\n"
    return boardPic

def sayBoard(board):
    # This function says board content.
    b = ""
    for i in range(1, 10):
        mark = convertLetterToWord(board[i])
        if mark in ["cross","nought"]:
            mark = "a " + mark
        b += convertBoardNumberToField(i) + " is " + mark + ". "
    return b

def clearBoard(attributes):
    attributes["board"] = [' '] * 10

def convertLetterToWord(l):
    if l=='X':
        return "cross"
    elif l=='O':
        return "nought"
    else:
        return "free"

def convertFieldToBoardNumber(f):
    fields = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
    return (fields.index(f) + 1)

def convertBoardNumberToField(n):
    fields = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
    return fields[n-1]

def makeMove(board, letter, index):
    board[index] = letter

def isWinner(b, l):
    # check if letter l won, i.e. has 3 in any possible combinations accross the board b
    winning_lines = [[7,8,9], [4,5,6], [1,2,3], [7,4,1], [8,5,2], [9,6,3], [7,5,3], [9,5,1]]
    for i in range(len(winning_lines)):
        if (b[winning_lines[i][0]] == l and b[winning_lines[i][1]] == l and b[winning_lines[i][2]] == l):
            return True
    return False

def getBoardCopy(board):
    # return a duplicate of the board
    return copy.deepcopy(board)

def isSpaceFree(board, move):
    # Return true if the passed move is free on the passed board.
    return board[move] == ' '

def getSpaceContent(board, move):
    # Return true if the passed move is free on the passed board.
    return board[move]

def isBoardFull(board):
    # Return True if every space on the board has been taken. Otherwise return False.
    for i in range(1, 10):
        if isSpaceFree(board, i):
            return False
    return True

def chooseRandomMoveFromList(board, movesList):
    # Returns a valid move from the passed list on the passed board.
    # Returns None if there is no valid move.
    possibleMoves = []
    for i in movesList:
        if isSpaceFree(board, i):
            possibleMoves.append(i)

    if len(possibleMoves) != 0:
        return choice(possibleMoves)
    else:
        return None

def getComputerMove(board, computerLetter):
    # Given a board and the computer's letter, determine where to move and return that move.
    if computerLetter == 'X':
        playerLetter = 'O'
    else:
        playerLetter = 'X'

    # Here is our algorithm for our Tic Tac Toe AI:
    # First, check if we can win in the next move
    for i in range(1, 10):
        copy = getBoardCopy(board)
        if isSpaceFree(copy, i):
            makeMove(copy, computerLetter, i)
            if isWinner(copy, computerLetter):
                return i

    # Check if the player could win on their next move, and block them.
    for i in range(1, 10):
        copy = getBoardCopy(board)
        if isSpaceFree(copy, i):
            makeMove(copy, playerLetter, i)
            if isWinner(copy, playerLetter):
                return i

    # Try to take one of the corners, if they are free.
    move = chooseRandomMoveFromList(board, [1, 3, 7, 9])
    if move != None:
        return move

    # Try to take the center, if it is free.
    if isSpaceFree(board, 5):
        return 5

    # Move on one of the sides.
    return chooseRandomMoveFromList(board, [2, 4, 6, 8])

def getAlexaMove(attributes):
    if (attributes["difficulty"] == "hard"):
        move = getComputerMove(attributes["board"], attributes["computer"])
    elif (attributes["difficulty"] == "medium"):
        # medioum difficuly means that the computer has a certain % chance to make a random move
        chance = randint(0, 100)
        #print(chance)
        if (chance > 60):
            move = chooseRandomMoveFromList(attributes["board"], [1,2,3,4,5,6,7,8,9])
        else:
            move = getComputerMove(attributes["board"], attributes["computer"])
    else:
        move = chooseRandomMoveFromList(attributes["board"], [1,2,3,4,5,6,7,8,9])
    return move

