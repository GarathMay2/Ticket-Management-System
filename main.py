# Author:       Garath May
# Class:        CS 361
# Title:        Main Program
# Description:  For my main program of the Ticket Management App, I chose to use
#               Streamlit as my method of creating all the UI elements I ended up
#               implementing. My reasoning is that the website showed some entirely
#               in-python website developement and I was sold instantly.
#
# Sources:      https://streamlit.io/playground
#               https://docs.streamlit.io/develop/concepts/architecture/forms
#               https://docs.python.org/3/library/pathlib.html
#
from pathlib import Path
import pandas as pd
import streamlit as st

TICKETS_PATH = Path(__file__).resolve().parent / "Tickets.csv"


# ticket template, descriptions and statuses left empty and will be changed to
# whatever those fields are once a ticket is submitted or closed, rspectively
def ticket(name,date,problem, description = "Blank"):
    return{
        "name": name,
        "date": date,
        "problem": problem,
        "description": description,
        "status": "Open"
    }

# adds a new instance of the ticket archive in case one does not exist
# it stores the tickets in a dictionary

# loads the filepath to where all the tickets are saved when a new session begins
if "ticket_archive" not in st.session_state:
    if TICKETS_PATH.exists() and TICKETS_PATH.stat().st_size > 0:
        saved_tickets = pd.read_csv(
            TICKETS_PATH,
            dtype=str,
            keep_default_na=False,
        )

        st.session_state.ticket_archive = (
            saved_tickets
            .set_index("ticket_id")
            .to_dict(orient="index")
        )
    else:
        st.session_state.ticket_archive = {}

# this will continue the numbering scheme in the CSV, basically meaning
#   if the last saved ticket was 4, the next saved ticket will be 5
existing_numbers = [
    int(ticket_id.removeprefix("Ticket #"))
    for ticket_id in st.session_state.ticket_archive
]

st.session_state.id_number = max(existing_numbers, default=0) + 1



# actually saves the update to the session
if "update_message" in st.session_state:
    st.success(st.session_state.pop("update_message"))



# when a user is done filling out the submit a ticket form, this function
# will be used to take whatever information they entered and create a ticket
# with it, saving it to the dictionary in the process.
# it also increments the id number by 1 since the id number will
# always be increasing
def create_ticket(name, date, problem, description = "Blank"):
    ticket_id = f"Ticket #{st.session_state.id_number}"

    st.session_state.ticket_archive[ticket_id] = ticket(
        name, date, problem, description
    )
    st.session_state.id_number += 1

    return ticket_id

# function to save the tickets
def save_tickets():
    rows = [
        {"ticket_id": ticket_id, **ticket_data}
        for ticket_id, ticket_data
        in st.session_state.ticket_archive.items()
    ]

    pd.DataFrame(
        rows,
        columns=[
            "ticket_id",
            "name",
            "date",
            "problem",
            "description",
            "status",
        ],
    ).to_csv(TICKETS_PATH, index=False)



# tabs
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Update a Ticket", "Search", "Contact Us"])



#
# HOME PAGE section
#
with tab1:
    st.title("Ticket Management Systems")
    st.write("Here you can create a ticket for our specialized teams "
                 "to review and complete. Once you have submitted a ticket, "
                 "you will recieve a Ticket ID and a confirmation that "
                 "your ticket was submitted!")
    col1, col2 = st.columns(2)


    # CREATE A TICKET BOX (submit a ticket to the CSV in the main.py folder)

    with col1:

        st.header('Create a Ticket', divider = 'gray')     # simple header

        with st.form("Create a Ticket"):                        # form creation, has text boxes in it
            new_name = st.text_input('Name (Required)')         # (Required) means theyre required
            new_date = st.date_input('Date (Required)')
            new_problem = st.text_input('Problem (Required)')
            new_description = st.text_area('Description (Optional)')
            submit = st.form_submit_button('Submit Ticket')     # submit button

        # Creates the save path for the csv that the ticket will be entered into
        if submit:
            if not new_name.strip() or not new_problem.strip(): # if a user left a field blank, error handling
                st.error("Please fill out the Required fields above")

            # rips the information entered and puts it in a ticket!
            else:
                ticket_id = create_ticket(
                    new_name.strip(),
                    new_date.isoformat(),
                    new_problem.strip(),
                    new_description.strip() or "Blank",
                )

                save_tickets()

                st.success(f"Ticket {ticket_id} Has Been Saved! You can view your ticket in the search tab!")




    # TICKET ARCHIVE box (shows the list of tickets in the CSV at that moment)

    with col2:
        st.header('Ticket Archive', divider = 'grey')


        # This displays the list of Tickets already saved in the archive
        with st.form("View Tickets"):
            # if the csv is empty or hasnt been created yet, this will display
            if not TICKETS_PATH.exists() or TICKETS_PATH.stat().st_size == 0:
                st.info("No tickets exist in the archive")
            else:
                tickets = pd.read_csv(TICKETS_PATH, dtype = str, keep_default_na = False)

                if tickets.empty:
                    st.info("No tickets exist in the archive")
                else:
                    # only displays the id, problem, and status and directs the user
                    # to the search page for more information on their tickets
                    st.dataframe(
                        tickets[["ticket_id", "problem", "status"]],
                        hide_index = True,
                        use_container_width = True
                    )
                    st.caption("For full details, please search for your"
                               "ticket in the Search Page")



#
# UPDATE TICKET Section
#
with tab2:
    st.header("Update a Ticket")
    st.subheader("Follow the directions below and fill out the form to update your ticket!")
    st.write("Select a Ticket you would like to update. "
             "Reminder: Changes are only saved after confirmation is made, "
             "and you can revert the last made change after confirmation.")

    @st.dialog("Ticket Update Form")
    def update(ticket_id):
        # grabs the ticket from the archive for updating
        current_ticket = st.session_state.ticket_archive[ticket_id]

        st.write(f"Updating {ticket_id}")

        # problem box
        problem = st.text_input(
            "Problem",
            value=current_ticket["problem"],
        )

        # desctiption box
        description = st.text_area(
            "Description",
            value=current_ticket["description"],
        )

        # status update box
        statuses = ["Open", "Closed"]
        status = st.selectbox(
            "Status",
            statuses,
            index=statuses.index(current_ticket["status"]),
        )

        # pop up for warning the user of their changes made
        warning = f"confirm_save{ticket_id}"

        if st.button("Save Changes"):
            st.session_state[warning] = True

        if st.session_state.get(warning, False):
            st.warning("Warning: Are you sure you want to make these changes?"
                       "Previous information in this ticket will be lost.")

            # options for the user to select, either they confirm or cancel their changes
            confirmation, cancel = st.columns(2)

            # if the user selects Yes, their changes will be saved and the warning will be
            # reset
            with confirmation:
                if st.button("Yes, Save Changes"):
                    # this will create a backup of the last change made
                    st.session_state.last_ticket_change = {
                        "ticket_id": ticket_id, "previous_data":(
                            st.session_state.ticket_archive[ticket_id].copy()
                        ),
                    }

                    st.session_state.ticket_archive[ticket_id].update({
                        "problem": problem,
                        "description": description,
                        "status": status
                    })

                    save_tickets()

                    st.session_state.pop(warning, None)
                    st.session_state.update_message = (f"{ticket_id} has been updated!")
                    st.rerun()

            # if they select No, they will be booted back from the dialog
            with cancel:
                if st.button("No"):
                    st.session_state.pop(warning, None)
                    st.rerun()

    # allows the user to revert back the last change they made
    if "last_ticket_change" in st.session_state:
        last_change = st.session_state.last_ticket_change
        undo_ticket_change = last_change["ticket_id"]

        if st.button(f"Revert previous change to {undo_ticket_change}"):
            # restores the save state which held the prior data to the ticket
            st.session_state.ticket_archive[undo_ticket_change] = (last_change["previous_data"].copy())

            save_tickets()

            # deletes the change
            del st.session_state["last_ticket_change"]

            st.session_state.update_message = (f"Previous change to Ticket {undo_ticket_change} reverted")
            st.rerun()


    # this is the dropdown menu for all the tickets the user can choose from the
    # CSV to update. I haven't determined whether or not this will be a user-end
    # function or not.
    if st.session_state.ticket_archive:
        selected_id = st.selectbox(
            "Choose a ticket to update",
            list(st.session_state.ticket_archive.keys()),
            key="ticket_to_update",
        )

        # opens the dialog
        if st.button("Update A Ticket"):
            update(selected_id)

    # this will pop up in the case of no ticket existing in the CSV
    else:
        st.info("Create a ticket before updating one.")

#
# SEARCH Section
#
with tab3:
    st.header("Search for a Ticket")
    st.write("Enter your Name or Ticket ID below and your ticket will be viewable!")

    # same with the update tab, this dialog will display the ticket in a similar format to the form
    # the user would have filled out when submitting a ticket.
    @st.dialog("Your Ticket")
    def display_ticket(matches):
        for i, ticket_data in matches.iterrows():
            ticket_id = ticket_data["ticket_id"]

            st.subheader(ticket_id)

            # name
            st.text_input("Name", value = ticket_data["name"], disabled = True, key = f"view_name_{ticket_id}")

            # date
            st.text_input("Date", value = ticket_data["date"], disabled = True, key = f"view_date_{ticket_id}")

            # problem
            st.text_input("Problem", value=ticket_data["problem"], disabled=True, key=f"view_problem_{ticket_id}")

            # description
            st.text_area("Description", value=ticket_data["description"], disabled=True, key=f"view_description_{ticket_id}")

            # status
            st.text_input("Status", value=ticket_data["status"], disabled=True, key=f"view_status_{ticket_id}")

            st.divider()

        if st.button("Close"):
            st.rerun()

    with st.form("Search Ticket Archive"):

        existing_id = st.number_input('Ticket ID#', min_value=0)
        st.write('-or-')
        existing_name = st.text_input('Name')

        search = st.form_submit_button('Search Ticket Archive')

    # user search functionality, returns the csv for the ticket
    if search:
        name = existing_name.strip()

        # error handling if user input isn't valid
        if existing_id == 0 and not name:
            st.error("Enter a valid Ticket ID or Name")

        # checks for the path, whether or not the path exists or if it's empty
        elif not TICKETS_PATH.exists() or TICKETS_PATH.stat().st_size == 0:
            st.info("No Tickets in the Archive")

        else:
            # makes a variable to act as the path and search function
            tickets = pd.read_csv(TICKETS_PATH, dtype=str, keep_default_na=False)

            # if the id exists, it links the match with the ticket id through its location in the path
            if existing_id:
                ticket_id = f"Ticket #{existing_id}"
                matches = tickets.loc[tickets["ticket_id"] == ticket_id]

            # selects the name column and searches it regardless of case,
            # saves all the matching one in matches
            else:
                matches = tickets.loc[tickets["name"].str.strip().str.casefold() == name.casefold()]

            # kind of error handling if the match wasnt found
            if matches.empty:
                st.info("No Matching Tickets Found")

            # displays the ticket the user searched for in a table format under the box
            else:
                display_ticket(matches)


#
# CONTACT US Section
#
with tab4:
    st.header("Contact Us!")
    st.write("IT Department: 555-555-5555")
    st.write("Engineering & Maintenance: 555-555-5555")









