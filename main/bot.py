# imports
from datetime import datetime
from HelperScripts.pdf_generator import generate_pdf
from HelperScripts.database_handler import DatabaseHandlers
import os
import re
import time
import telebot

# Define your bot token here
BOT_TOKEN = "bot_token"

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["help", "h"])
def help(message):

    """
    This function will send the link of documentation to the user.

    Args:
        message: The message sent by the user

    Returns:
        None
    """
    bot.reply_to(
        message,
        "You can find the documentation of the bot here : https://github.com/haaris272k/ExpenseGenie/blob/main/README.md."
        " You can get detailed information about the bot and its usage.",
    )


@bot.message_handler(commands=["list", "l"])
def list_available_commands(message):

    """
    This function will list all the available commands of the bot.

    Args:
        message: The message sent by the user

    Returns:
        None
    """
    bot.reply_to(
        message,
        "Available commands : \n\n"
        " /help - To get detailed information \n\n /start - To start the bot \n\n /add - To add an expense \n\n"
        " /view - To view the expenses \n\n /total - To view the total expense"
        + "\n\n /delete - To delete an expense or all the expenses"
        "\n\n (Tip : You can use initial letters of the commands too.\n\n For example, /s for /start, /a for /add, and so on.)",
    )


@bot.message_handler(commands=["start", "s"])
def start(message):

    """
    This function sends a welcome message to the user.
    It also checks if the user is already registered or not. If the user is not registered,
    it will register the user in the database.

    Args:
        message: The message sent by the user

    Returns:
        None
    """
    try:
        # Database object
        dbobj = DatabaseHandlers()

        # Connecting to the database
        dbobj.connect_database()

        # Getting user name
        username = message.from_user.username

        # checking if username is None then send the message to the user to immediately set the username in the telegram account
        if username is None:

            # Sending the message to the user
            bot.reply_to(
                message,
                "<b>Important❗</b>"
                "\n\nIt looks like you have not set a <b>username</b> in your telegram account."
                " Please set a username in the <b>settings</b> section of your telegram account and then enter the /start command again."
                "\n\nFYI, Username is different from the display name."
                " Username is the one which is shown after the @ symbol in your telegram account.",
                parse_mode="HTML",
            )
            # Exiting the function
            return

        # Replying to the user
        bot.reply_to(
            message,
            f"Good to see you, {username}. With the BudgetWizardBot , you can easily keep track of all your expenses."
            " You will be registered automatically if you are not registered. Feel free to use /list command to see all the available commands.",
        )

        # Wait
        time.sleep(0.5)

        # Checking if the user is already registered or not
        if dbobj.collection.find_one(
            {"username": username}
        ):

            bot.reply_to(
                message,
                f"Hey {username}! You are already registered!. You can start using the bot.",
            )

        else:

            bot.reply_to(
                message,
                "You were not registered, so I have automatically registered you."
                " Please remember your username and don't change it in the future.",
            )

    except:

        bot.reply_to(
            message,
            "There was some error. Developer is working on it. Please try again later.",
        )


@bot.message_handler(commands=["add", "a"])
def add_expense(message):

    """
    This function will add the expense to the database corresponding to the unique username.

    Args:
        message: The message sent by the user

    Returns:
        None
    """
    try:
        # Database object
        dbobj = DatabaseHandlers()

        # Getting username
        username = message.from_user.username

        # checking if username is None then send the message to the user to immediately set the username in the telegram account
        if username is None:

            # Sending the message to the user
            bot.reply_to(
                message,
                "<b>Important❗</b>"
                "\n\nIt looks like you have not set a username in your telegram account even after the reminder."
                " Therefore, you were not registered and no data is available for you."
                " Please set a username in the settings section of your telegram as notifed earlier to, further use the bot.",
                parse_mode="HTML",
            )
            # Exiting the function
            return

        # Getting user ID
        user_id = message.from_user.id

        # Asking user to enter the expense
        bot.reply_to(message, "Please enter the expense")

        # Waiting for the user to enter the expense
        bot.register_next_step_handler(message, get_expense, dbobj, username, user_id)

    except:
        # Sending the error message to the user
        bot.send_animation(
            message.chat.id,
            "https://media.giphy.com/media/JT7Td5xRqkvHQvTdEu/giphy.gif",
            caption="Sorry, I didn't understand your input or you may have entered the command without replying to the previous message."
            " Please try again with a valid command.",
        )


def get_expense(message, dbobj, username, user_id):

    """
    This function will get the expense from the user

    Args:
        message: The message sent by the user
        dbobj: The database object
        username: The username of the user

    Returns:
        None
    """
    try:
        # Getting the expense from the user
        expense = message.text

        # Parsing the expense to get the amount, just in case the user enters with some extra characters
        # Using regex to get only the numbers
        expense = re.findall(r"\d+", expense)[0]

        # Asking user to enter the tag
        bot.reply_to(message, "Please enter the tag")

        # Waiting for the user to enter the tag
        bot.register_next_step_handler(
            message, get_tag, dbobj, username, user_id, expense
        )

    except:
        # Sending the error message to the user
        bot.send_animation(
            message.chat.id,
            "https://media.giphy.com/media/JT7Td5xRqkvHQvTdEu/giphy.gif",
            caption="Sorry, I didn't understand your input or you may have entered the command without replying to the previous message."
            " Please try again with a valid command.",
        )


def get_tag(message, dbobj, username, user_id, expense):

    """
    This function will get the tag from the user

    Args:
        message: The message sent by the user
        dbobj: The database object
        username: The username of the user
        expense: The expense entered by the user

    Returns:
        None
    """
    try:
        # Getting the tag from the user
        tag = message.text

        # Well formatted timestamp
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Connecting to the database
        dbobj.connect_database()

        # Define a function to get the current max id value
        def get_max_id():
            result = dbobj.collection.find_one(
                {}, sort=[("id", -1)], projection={"id": True}
            )
            return result["id"] if result else 0

        # Define a function to insert a new document with an auto-incrementing id value
        def insert_document(document):
            document["id"] = get_max_id() + 1
            dbobj.collection.insert_one(document)

        # Forming the data to be inserted in the database
        expense_data = {
            "username": username,
            "u_id": user_id,
            "expense": expense,
            "tag": tag,
            "timestamp": timestamp,
        }
        insert_document(expense_data)

        # Closing the connection to the database
        dbobj.close_database()

        # Sending confirmation message to the user
        bot.reply_to(message, "Expense added successfully!")

    except:
        bot.reply_to(
            message,
            "There was some error. Developer is working on it. Please try again later.",
        )


@bot.message_handler(commands=["view", "v"])
def view_expense(message):

    """
    This function will view the expense of the user.

    Args:
        message: The message sent by the user

    Returns:
        None
    """
    dboj = DatabaseHandlers()
    dboj.connect_database()

    # Getting username
    username = message.from_user.username

    # Getting user ID
    user_id = message.from_user.id

    # asking the user to wait
    bot.reply_to(message, "Please wait while I fetch your data...")

    # Getting the data from the database corresponding to the username and user ID
    query = {"username": username, "u_id": user_id}

    # Getting the data from the database
    data = dboj.collection.find(query)

    # Checking if user has set the username in the telegram account
    if username is None:

        # Sending the message to the user
        bot.reply_to(
            message,
            "<b>Important❗</b>"
            "\n\nIt looks like you have not set a username in your telegram account even after the reminder."
            " Therefore, you were not registered and no data is available for you."
            " Please set a username in the settings section of your telegram as notifed earlier to, further use the bot.",
            parse_mode="HTML",
        )

    else:
        # Using generate pdf function to generate the pdf and sending it to the user
        generate_pdf(data, username)

        # Sending the pdf to the user
        with open(f"{username}.pdf", "rb") as pdf:
            bot.send_document(message.chat.id, pdf)

        # Deleting the pdf from the server
        os.remove(f"{username}.pdf")


@bot.message_handler(commands=["total", "t"])
def total_expense(message):

    """
    This function will view the total expense of the user as per the users choice of
    getting the overall total expense or the total expense of the current month.

    Args:
        message: The message sent by the user

    Returns:
        None
    """
    # Database object
    dbobj = DatabaseHandlers()

    # Connecting to the database
    dbobj.connect_database()

    # Getting username
    username = message.from_user.username

    # Getting user ID
    user_id = message.from_user.id

    # Asking user to enter the choice
    bot.reply_to(
        message,
        "Please enter the choice. \n\n 1. Overall total \n\n 2. Total of the current month",
    )

    # Waiting for the user to enter the choice
    bot.register_next_step_handler(message, get_choice, dbobj, username, user_id)


def get_choice(message, dbobj, username, user_id):

    """
    This function will get the choice from the user i.e. whether
    the user wants to get the 'overall' total expense or the total expense of the 'current month'.

    Args:
        message: The message sent by the user
        dbobj: The database object
        username: The username of the user

    Returns:
        None
    """
    try:
        # Checking if the user has set a username or not
        if username is None:

            # Sending the message to the user
            bot.reply_to(
                message,
                "<b>Important❗</b>"
                "\n\nIt looks like you have not set a username in your telegram account even after the reminder."
                " Therefore, you were not registered and no data is available for you."
                " Please set a username in the settings section of your telegram as notifed earlier to, further use the bot.",
                parse_mode="HTML",
            )

        else:
            # Getting the choice from the user
            choice = message.text

            # Checking if the choice is valid or not
            if choice not in ["1", "2"]:
                bot.reply_to(
                    message,
                    "Invalid choice. Please re-enter the command and enter a valid choice.",
                )
                return

            # Getting the current month
            current_month = datetime.now().strftime("%m")

            # Getting the current year
            current_year = datetime.now().strftime("%Y")

            # Getting the data from the database
            query = {"username": username, "u_id": user_id}

            # Getting the data from the database
            data = dbobj.collection.find(query)

            # Total expense
            total_expense = 0

            # Checking if the choice is 1 or 2
            if choice == "1":

                # Iterating over the data
                for i in data:

                    # Adding the expense to the total expense
                    total_expense += int(i["expense"])

                # Sending the total expense to the user
                bot.reply_to(
                    message,
                    f"Your overall total expense is <b>{total_expense}</b>",
                    parse_mode="HTML",
                )

            else:

                # Iterating over the data
                for i in data:

                    # Getting the month from the timestamp
                    month = i["timestamp"].split("-")[1]

                    # Getting the year from the timestamp
                    year = i["timestamp"].split("-")[2].split(" ")[0]

                    # Checking if the month and year is same as the current month and year
                    if month == current_month and year == current_year:

                        # Adding the expense to the total expense
                        total_expense += int(i["expense"])

                # Sending the total expense to the user
                bot.reply_to(
                    message,
                    f"Your total expense for this month is <b>{total_expense}</b>",
                    parse_mode="HTML",
                )

    except:
        bot.reply_to(message, "There was some error.")


@bot.message_handler(commands=["delete", "d"])
def delete_expense(message):

    """
    This function will delete the expense of the user. The user will have to enter the id of the expense
    that he wants to delete or he can enter 'all' to delete all the expenses.

    Args:
        message: The message sent by the user

    Returns:
        None
    """
    # Database object
    dbobj = DatabaseHandlers()

    # Connecting to the database
    dbobj.connect_database()

    # Getting username
    username = message.from_user.username

    # Getting user ID
    user_id = message.from_user.id

    # Asking user to enter the choice
    bot.reply_to(
        message,
        f"Please enter the choice. \n\n 1. Delete all expenses \n\n 2. Delete a specific expense. \n\n"
        " <b>Warning: Action once done cannot be undone❗</b>",
        parse_mode="HTML",
    )

    # Waiting for the user to enter the choice
    bot.register_next_step_handler(message, get_delete_choice, dbobj, username, user_id)


def get_delete_choice(message, dbobj, username, user_id):

    """
    This function will get the choice from the user i.e. whether
    the user wants to delete all the expenses or a specific expense.

    Args:
        message: The message sent by the user
        dbobj: The database object
        username: The username of the user

    Returns:
        None
    """
    try:

        if username is None:

            # Sending the message to the user
            bot.reply_to(
                message,
                "<b>Important❗</b>"
                "\n\nIt looks like you have not set a username in your telegram account even after the reminder."
                " Therefore, you were not registered and no data is available for you."
                " Please set a username in the settings section of your telegram as notifed earlier to, further use the bot.",
                parse_mode="HTML",
            )

        else:
            # Getting the choice from the user
            choice = message.text

            # Checking if the choice is valid or not
            if choice not in ["1", "2"]:
                bot.reply_to(
                    message,
                    "Invalid choice. Please re-enter the command and enter a valid choice.",
                )
                return

            # Checking if the choice is 1 or 2
            if choice == "1":

                # Deleting all the expenses of the user
                query = {"username": username, "u_id": user_id}
                dbobj.collection.delete_many(query)

                # Sending the confirmation message to the user
                bot.reply_to(
                    message, "All the expenses have been deleted successfully!"
                )

            else:

                # Asking the user to enter the id of the expense that he wants to delete
                bot.reply_to(
                    message,
                    "Please enter the id of the expense that you want to delete. I will send your expense data for reference.",
                )

                time.sleep(1)

                view_expense(message)

                # Waiting for the user to enter the id
                bot.register_next_step_handler(
                    message, get_id, dbobj, username, user_id
                )

    except:
        bot.reply_to(message, "There was some error.")


def get_id(message, dbobj, username, user_id):

    """
    This function will get the id of the expense that the user wants to delete.

    Args:
        message: The message sent by the user
        dbobj: The database object
        username: The username of the user

    Returns:
        None
    """
    try:
        # Getting the id from the user
        id = message.text

        # Checking if id is a valid integer
        if not id.isdigit():
            bot.reply_to(message, "Please enter a valid id.")
            return

        # Deleting the expense from the database
        query = {"username": username, "u_id": user_id, "id": int(id)}
        result = dbobj.collection.delete_one(query)

        # Checking if a document was deleted or not
        if result.deleted_count == 0:
            bot.reply_to(message, "No expense found with the entered id.")
        else:
            bot.reply_to(message, "The expense has been deleted successfully!")

    except:
        bot.reply_to(message, "There was some error.")


@bot.message_handler(func=lambda m: True)
def invalid_input(message):

    """
    function to handle invalid input
    Args:
        message (str): message sent by the user
    Returns:
        None

    """
    # sending 'invalid input!' message to the user along with the gif
    bot.send_animation(
        message.chat.id,
        "https://tenor.com/bMVFk.gif",
        caption="Error! This occurred because you may have entered one of the following."
        "<b>\n\n- An invalid command\n\n- An input without using a command.</b>",
        parse_mode="HTML",
    )


def main():

    """
    This function will run the bot
    Args:
        None
    Returns:
        None
    """
    # Running the bot
    bot.infinity_polling()


if __name__ == "__main__":
    main()

