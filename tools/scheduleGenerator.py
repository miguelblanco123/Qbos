import pandas as pd
import streamlit as st
import math
from datetime import datetime, timedelta

# Initialize all session state variables at the start
def initialize_session_state():
    if 'selected_categories' not in st.session_state:
        st.session_state.selected_categories = []
    if 'number_of_competitors' not in st.session_state:
        st.session_state.number_of_competitors = 1
    if 'rounds_cutoffs' not in st.session_state:
        st.session_state.rounds_cutoffs = {}
    if 'main_event' not in st.session_state:
        st.session_state.main_event = '3x3'
    if 'num_days' not in st.session_state:
        st.session_state.num_days = 2
    if 'day_schedules' not in st.session_state:
        st.session_state.day_schedules = [('09:00', '18:00')] * 2
        

categories = ['3x3', '2x2', '4x4', '5x5', '6x6', '7x7', '3BLD', '3OH', 'FMC', 
              'Megaminx', 'Pyraminx', 'Skewb', 'Square-1', 'Clock', '4BLD', 
              '5BLD', 'MBLD']

# Dictionary of registration percentages with exact values
registration_percentages = {
    '2x2': 83.92,
    '3x3': 97.49,
    '3BLD': 33.15,
    'FMC': 71.45,
    '3OH': 69.03,
    '4x4': 69.17,
    '4BLD': 19.94,
    '5x5': 59.59,
    '5BLD': 13.00,
    '6x6': 44.54,
    '7x7': 44.98,
    'Clock': 53.57,
    'Megaminx': 58.59,
    'Pyraminx': 72.37,
    'Skewb': 60.80,
    'Square-1': 39.63,
    'MBLD': 10.00
}

# Format and attempts for each category
event_details = {
    '3x3': {'format': 'Ao5', 'attempts': 5, 'scramble_time': 30},
    '2x2': {'format': 'Ao5', 'attempts': 5, 'scramble_time': 20},
    '4x4': {'format': 'Ao5', 'attempts': 5, 'scramble_time': 40},
    '5x5': {'format': 'Ao5', 'attempts': 5, 'scramble_time': 50},
    '6x6': {'format': 'Mo3', 'attempts': 3, 'scramble_time': 50},
    '7x7': {'format': 'Mo3', 'attempts': 3, 'scramble_time': 50},
    'Megaminx': {'format': 'Ao5', 'attempts': 5, 'scramble_time': 60},
    'Pyraminx': {'format': 'Ao5', 'attempts': 5, 'scramble_time': 30},
    'Square-1': {'format': 'Ao5', 'attempts': 5, 'scramble_time': 30},
    'Clock': {'format': 'Ao5', 'attempts': 5, 'scramble_time': 40},
    'Skewb': {'format': 'Ao5', 'attempts': 5, 'scramble_time': 20},
    '3OH': {'format': 'Ao5', 'attempts': 5, 'scramble_time': 30},
    '3BLD': {'format': 'Mo3', 'attempts': 3, 'scramble_time': 360},
    'FMC': {'format': 'Mo3', 'attempts': 3, 'scramble_time': 0},
    '4BLD': {'format': 'Mo3', 'attempts': 3, 'scramble_time': 0},
    '5BLD': {'format': 'Mo3', 'attempts': 3, 'scramble_time': 0},
    'MBLD': {'format': 'Single', 'attempts': 1, 'scramble_time': 0}
}

# Categories that need triple station capacity for groups
small_categories = {'2x2', '3x3', '3OH', 'Skewb', 'Pyraminx'}
# Categories that always have one group
single_group_categories = {'FMC', '4BLD', '5BLD', 'MBLD'}
# Categories with fixed time
fixed_time_categories = {'FMC', '4BLD', '5BLD', 'MBLD'}

def get_default_settings():
    """Return default settings for a new category"""
    return {
        'rounds': 1,
        'cutoff': 'None',
        'advance_r1': 75,  # Default 75% advance from first round
        'advance_r2': 50,  # Default 50% advance from second round
        'advance_r3': 25,  # Default 25% advance from third round
    }

def round_up_to_15_minutes(minutes):
    """Round up to nearest 15 minutes"""
    return math.ceil(minutes / 15) * 15

def minutes_to_hhmm(minutes):
    """Convert minutes to HH:MM format"""
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{int(hours):02d}:{int(remaining_minutes):02d}"

def calculate_round_time(category, num_competitors, num_stations, cutoff=None, is_first_round=True):
    """Calculate the estimated round time in minutes"""
    
    # Fixed time categories always take 75 minutes
    if category in fixed_time_categories:
        return 75
    
    # Get event details
    details = event_details[category]
    default_time = 35  # Default solving time in seconds
    
    if cutoff and cutoff != 'None':
        # Convert cutoff string to seconds if it's in MM:SS format
        if isinstance(cutoff, str) and ':' in cutoff:
            minutes, seconds = map(int, cutoff.split(':'))
            cutoff_seconds = minutes * 60 + seconds
            # Use 70% of cutoff time for first round, 60% for subsequent rounds
            solving_time = cutoff_seconds * (0.7 if is_first_round else 0.6)
        else:
            solving_time = default_time
    else:
        solving_time = default_time
    
    # Calculate total time per solve
    total_time_per_solve = solving_time + details['scramble_time']
    
    # Calculate total round time in minutes
    total_seconds = (total_time_per_solve * details['attempts'] * num_competitors) / (num_stations - 3)
    total_minutes = total_seconds / 60
    
    # Round up to nearest 15 minutes
    return round_up_to_15_minutes(total_minutes)

def round_up_to_5(number):
    """Round up to nearest 5"""
    return math.ceil(number / 5) * 5

def calculate_stations(total_competitors):
    """Calculate the number of stations needed"""
    # Calculate base number of stations (2 stations per 20 competitors)
    base_stations = math.ceil(total_competitors / 20) * 2
    
    # Ensure minimum of 6 stations
    if base_stations < 6:
        return 6
    
    # Round up to nearest even number if necessary
    return math.ceil(base_stations / 2) * 2

def calculate_groups_and_size(category, competitors, num_stations):
    """Calculate the number of groups and size per group"""
    if category in single_group_categories:
        return 1, competitors
    
    # Calculate max competitors per group based on category type
    if category in small_categories:
        max_per_group = num_stations * 3
    else:
        max_per_group = num_stations * 2
    
    # Calculate number of groups needed
    num_groups = math.ceil(competitors / max_per_group)
    # Calculate actual group size
    group_size = math.ceil(competitors / num_groups)
    
    return num_groups, group_size

def validate_rounds(num_competitors, proposed_rounds):
    """
    Validate if the number of rounds is allowed based on WCA regulations
    Returns (is_valid, message)
    """
    if num_competitors <= 7:
        return (1, "7 or fewer competitors can only have 1 round")
    elif num_competitors <= 15:
        return (min(2, proposed_rounds), "15 or fewer competitors can have maximum 2 rounds")
    elif num_competitors <= 99:
        return (min(3, proposed_rounds), "99 or fewer competitors can have maximum 3 rounds")
    return (proposed_rounds, "")

def get_default_settings():
    """Return default settings for a new category"""
    return {
        'rounds': 1,
        'cutoff': 'None',
        'advance_r1': 50,  # Default 75% advance from first round
        'advance_r2': 50,  # Default 75% advance from second round
        'advance_r3': 50,  # Default 75% advance from third round
        'final_size': 8    # Default final size
    }

def calculate_estimated_competitors(total_competitors, selected_categories, rounds_cutoffs):
    """Calculate estimated competitors and related metrics for each category"""
    num_stations = calculate_stations(total_competitors)
    estimates = []
    
    for category in selected_categories:
        if category in registration_percentages:
            settings = rounds_cutoffs[category]
            initial_competitors = round_up_to_5((registration_percentages[category] / 100) * total_competitors)
            
            # Validate number of rounds based on initial competitors
            allowed_rounds, message = validate_rounds(initial_competitors, settings.get('rounds', 1))
            if allowed_rounds != settings.get('rounds', 1):
                settings['rounds'] = allowed_rounds
                st.sidebar.warning(f"{category}: {message}")
            
            num_rounds = settings.get('rounds', 1)
            cutoff = settings.get('cutoff', 'None')
            
            # Calculate first round
            num_groups, group_size = calculate_groups_and_size(category, initial_competitors, num_stations)
            round1_time = calculate_round_time(category, initial_competitors, num_stations, cutoff, True)
            
            row_data = {
                'Category': category,
                'Percentage': f"{registration_percentages[category]}%",
                'R1 Competitors': initial_competitors,
                'R1 Groups': num_groups,
                'R1 Time': minutes_to_hhmm(round1_time)
            }
            
            current_competitors = initial_competitors
            for round_num in range(2, num_rounds + 1):
                is_final = (round_num == num_rounds and num_rounds > 1)
                
                if is_final:
                    # For finals, use fixed number
                    final_size = settings.get('final_size', 8)
                    # Ensure final size is not too large (max 75% of previous round)
                    max_final_size = math.floor(current_competitors * 0.75)
                    current_competitors = min(final_size, max_final_size)
                else:
                    # For other rounds, use percentage
                    advance_key = f'advance_r{round_num-1}'
                    advance_percent = settings.get(advance_key, 75)
                    # Ensure at least 25% are eliminated
                    advance_percent = min(75, advance_percent)
                    current_competitors = round_up_to_5(current_competitors * (advance_percent / 100))
                
                num_groups, group_size = calculate_groups_and_size(category, current_competitors, num_stations)
                round_time = calculate_round_time(category, current_competitors, num_stations, cutoff, False)
                
                round_prefix = f'R{round_num}'
                row_data[f'{round_prefix} Competitors'] = current_competitors
                row_data[f'{round_prefix} Groups'] = num_groups
                row_data[f'{round_prefix} Time'] = minutes_to_hhmm(round_time)
            
            estimates.append(row_data)
    
    return pd.DataFrame(estimates)

def reset_settings():
    """Reset all settings to default values"""
    st.session_state.selected_categories = []
    st.session_state.number_of_competitors = 1
    st.session_state.rounds_cutoffs = {}

def update_selected_categories():
    """Callback for multiselect to update session state"""
    st.session_state.selected_categories = st.session_state.categories_select
    # Initialize settings for new categories
    for category in st.session_state.selected_categories:
        if category not in st.session_state.rounds_cutoffs:
            st.session_state.rounds_cutoffs[category] = get_default_settings()

def update_competitor_count():
    """Callback for number input to update session state"""
    st.session_state.number_of_competitors = st.session_state.competitor_count

def on_rounds_change(category):
    """Callback for rounds number input"""
    key = f'rounds_{category}'
    if key in st.session_state:
        if category not in st.session_state.rounds_cutoffs:
            st.session_state.rounds_cutoffs[category] = get_default_settings()
        st.session_state.rounds_cutoffs[category]['rounds'] = st.session_state[key]

def on_cutoff_change(category):
    """Callback for cutoff text input"""
    key = f'cutoff_{category}'
    if key in st.session_state:
        if category not in st.session_state.rounds_cutoffs:
            st.session_state.rounds_cutoffs[category] = get_default_settings()
        st.session_state.rounds_cutoffs[category]['cutoff'] = st.session_state[key]

def on_advance_change(category, advance_key):
    """Callback for advancement percentage input"""
    key = f'{advance_key}_{category}'
    if key in st.session_state:
        if category not in st.session_state.rounds_cutoffs:
            st.session_state.rounds_cutoffs[category] = get_default_settings()
        st.session_state.rounds_cutoffs[category][advance_key] = st.session_state[key]
        
def on_final_size_change(category):
    """Callback for final round size input"""
    key = f'final_size_{category}'
    if key in st.session_state:
        if category not in st.session_state.rounds_cutoffs:
            st.session_state.rounds_cutoffs[category] = get_default_settings()
        st.session_state.rounds_cutoffs[category]['final_size'] = st.session_state[key]
        
        
def get_day_schedule(day_start, day_end):
    """Convert time strings to minutes from midnight"""
    start_h, start_m = map(int, day_start.split(':'))
    end_h, end_m = map(int, day_end.split(':'))
    return start_h * 60 + start_m, end_h * 60 + end_m

def minutes_to_time(minutes):
    """Convert minutes from midnight to HH:MM format"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{int(hours):02d}:{int(mins):02d}"

def schedule_competition(estimates_df, num_days, day_schedules, main_event, rounds_cutoffs):
    """
    Schedule all competition rounds across multiple days
    """
    warnings = []
    schedule = []
    
    # First, organize all events and rounds
    all_events = []
    
    # Process round 1 for all events first
    for _, row in estimates_df.iterrows():
        category = row['Category']
        if 'R1 Time' in row and pd.notna(row['R1 Time']):
            time_str = row['R1 Time']
            hours, minutes = map(int, time_str.split(':'))
            duration = hours * 60 + minutes
            
            all_events.append({
                'category': category,
                'round': 1,
                'duration': duration,
                'competitors': row['R1 Competitors'],
                'is_main': category == main_event,
                'is_popular': category in {'2x2', '3x3', '4x4', '3OH', 'Pyraminx', 'Skewb'},
                'is_fmc': category == 'FMC'
            })
    
    # Then process round 2 for all events
    for _, row in estimates_df.iterrows():
        category = row['Category']
        if 'R2 Time' in row and pd.notna(row['R2 Time']):
            time_str = row['R2 Time']
            hours, minutes = map(int, time_str.split(':'))
            duration = hours * 60 + minutes
            
            all_events.append({
                'category': category,
                'round': 2,
                'duration': duration,
                'competitors': row['R2 Competitors'],
                'is_main': category == main_event,
                'is_popular': category in {'2x2', '3x3', '4x4', '3OH', 'Pyraminx', 'Skewb'},
                'is_fmc': category == 'FMC'
            })
    
    # Finally process round 3 for all events
    for _, row in estimates_df.iterrows():
        category = row['Category']
        if 'R3 Time' in row and pd.notna(row['R3 Time']):
            time_str = row['R3 Time']
            hours, minutes = map(int, time_str.split(':'))
            duration = hours * 60 + minutes
            
            # If this is the main event final, save it for last
            if category == main_event:
                main_final = {
                    'category': category,
                    'round': 3,
                    'duration': duration,
                    'competitors': row['R3 Competitors'],
                    'is_main': True,
                    'is_popular': category in {'2x2', '3x3', '4x4', '3OH', 'Pyraminx', 'Skewb'},
                    'is_fmc': category == 'FMC'
                }
            else:
                all_events.append({
                    'category': category,
                    'round': 3,
                    'duration': duration,
                    'competitors': row['R3 Competitors'],
                    'is_main': category == main_event,
                    'is_popular': category in {'2x2', '3x3', '4x4', '3OH', 'Pyraminx', 'Skewb'},
                    'is_fmc': category == 'FMC'
                })
    
    # Add main event final at the end if it exists
    if 'main_final' in locals():
        all_events.append(main_final)
    
    # Sort popular events within each round group to be later
    events_to_schedule = all_events
    
    # Initialize day schedules
    current_day = 1
    current_event_index = 0
    
    for day in range(1, num_days + 1):
        day_start, day_end = get_day_schedule(*day_schedules[day - 1])
        current_time = day_start
        
        # Add registration period for day 1
        if day == 1:
            schedule.append({
                'Day': day,
                'Start': minutes_to_time(current_time),
                'End': minutes_to_time(current_time + 45),
                'Event': 'Registration',
                'Round': '-',
                'Duration': '00:45'
            })
            current_time += 45
        
        # Calculate lunch break time (halfway through the day)
        lunch_time = day_start + (day_end - day_start) // 2
        lunch_added = False
        
        # Schedule events for the day
        while current_event_index < len(events_to_schedule) and current_time < day_end:
            # Check if it's time for lunch break
            if not lunch_added and current_time >= lunch_time:
                schedule.append({
                    'Day': day,
                    'Start': minutes_to_time(current_time),
                    'End': minutes_to_time(current_time + 60),
                    'Event': 'Lunch Break',
                    'Round': '-',
                    'Duration': '01:00'
                })
                current_time += 60
                lunch_added = True
                continue
            
            event = events_to_schedule[current_event_index]
            
            # Check if event can fit in remaining time
            if current_time + event['duration'] <= day_end:
                schedule.append({
                    'Day': day,
                    'Start': minutes_to_time(current_time),
                    'End': minutes_to_time(current_time + event['duration']),
                    'Event': event['category'],
                    'Round': f"Round {event['round']}",
                    'Duration': minutes_to_hhmm(event['duration'])
                })
                current_time += event['duration']
                current_event_index += 1
            else:
                break
        
        # Add prize giving on last day if all events are scheduled
        if day == num_days and current_event_index >= len(events_to_schedule):
            if current_time + 30 <= day_end:
                schedule.append({
                    'Day': day,
                    'Start': minutes_to_time(current_time),
                    'End': minutes_to_time(current_time + 30),
                    'Event': 'Prize Giving',
                    'Round': '-',
                    'Duration': '00:30'
                })
        
        # Check if day is too long
        day_duration = current_time - day_start
        if day_duration > 540:  # 9 hours (8 hours + 1 hour lunch)
            warnings.append(f"Day {day} is longer than recommended (9 hours). Consider removing some events or rounds.")
    
    # Check for unscheduled events
    if current_event_index < len(events_to_schedule):
        warnings.append("Not all events could be scheduled. Consider:")
        warnings.append("- Removing some events")
        warnings.append("- Adding more days")
        warnings.append("- Reducing number of rounds")
        warnings.append("- Adjusting cutoffs to reduce round durations")
    
    return pd.DataFrame(schedule), warnings

def display_schedule(schedule_df):
    # Group the schedule by days
    days = schedule_df['Day'].unique()
    
    for day in days:
        day_schedule = schedule_df[schedule_df['Day'] == day]
        
        st.subheader(f"Day {int(day)}")
        
        # Create columns for each field we want to display
        cols = st.columns([2, 3, 3, 4])
        cols[0].markdown("**Time**")
        cols[1].markdown("**Event**")
        cols[2].markdown("**Round**")
        cols[3].markdown("**Duration**")
        
        # Add a divider
        st.markdown("---")
        
        for _, row in day_schedule.iterrows():
            cols = st.columns([2, 3, 3, 4])
            
            # Time column: combine start and end time
            time_str = f"{row['Start']} - {row['End']}"
            cols[0].write(time_str)
            
            # Event name
            if row['Event'] in ['Registration', 'Lunch Break', 'Prize Giving']:
                cols[1].markdown(f"**{row['Event']}**")
            else:
                cols[1].write(row['Event'])
            
            # Round number
            cols[2].write(row['Round'])
            
            # Duration
            cols[3].write(row['Duration'])
            
        # Add some spacing between days
        st.markdown("\n")
        
        
def scheduleGenerator():
    # Initialize session state first
    initialize_session_state()
    
    st.title('Schedule Generator')
    st.write('Welcome to the Schedule Generator app')
    
    # Add reset button in the sidebar
    if st.sidebar.button('Reset All Settings'):
        reset_settings()
        st.experimental_rerun()
    
    # Add number of days selection at the top of the sidebar
    num_days = st.sidebar.number_input(
        'Number of Competition Days', 
        min_value=1, 
        max_value=3, 
        value=st.session_state.num_days,
        key='days_input'
    )
    st.session_state.num_days = num_days
    
    # Category selection
    selected_categories = st.sidebar.multiselect(
        'Select Categories',
        categories,
        key='categories_select',
        default=st.session_state.selected_categories,
        on_change=update_selected_categories
    )
    
    # Main event selection (only show if categories are selected)
    if selected_categories:
        main_event = st.sidebar.selectbox(
            'Main Event',
            selected_categories,
            index=selected_categories.index('3x3') if '3x3' in selected_categories else 0,
            key='main_event_select'
        )
        st.session_state.main_event = main_event
    
    # Number of competitors input
    number_of_competitors = st.sidebar.number_input(
        'Number of Competitors',
        min_value=1,
        value=st.session_state.number_of_competitors,
        key='competitor_count',
        on_change=update_competitor_count
    )
    
    # Add day schedule inputs
    day_schedules = []
    for day in range(num_days):
        st.sidebar.subheader(f'Day {day + 1} Schedule')
        col1, col2 = st.sidebar.columns(2)
        with col1:
            default_start = datetime.strptime(st.session_state.day_schedules[day][0], '%H:%M').time()
            start_time = st.time_input(f'Day {day + 1} Start Time', value=default_start)
        with col2:
            default_end = datetime.strptime(st.session_state.day_schedules[day][1], '%H:%M').time()
            end_time = st.time_input(f'Day {day + 1} End Time', value=default_end)
        day_schedules.append((start_time.strftime('%H:%M'), end_time.strftime('%H:%M')))
    st.session_state.day_schedules = day_schedules

    # Calculate stations
    num_stations = calculate_stations(number_of_competitors)
    
    # Create two columns for KPIs
    col1, col2 = st.columns(2)
    
    # Display KPIs
    with col1:
        st.metric(
            label="Total Competitors",
            value=number_of_competitors
        )
    with col2:
        st.metric(
            label="Solving Stations Required",
            value=num_stations,
            help="2 stations per 20 competitors, minimum 6 stations"
        )
    
    # Add a divider
    st.markdown("---")
    
    # Settings for each category
    for category in selected_categories:
        if category not in st.session_state.rounds_cutoffs:
            st.session_state.rounds_cutoffs[category] = get_default_settings()
            
        with st.sidebar.expander(f'{category} Settings'):
            saved_settings = st.session_state.rounds_cutoffs[category]
            initial_competitors = round_up_to_5((registration_percentages[category] / 100) * number_of_competitors)
            
            # Calculate maximum allowed rounds
            max_allowed_rounds, message = validate_rounds(initial_competitors, 4)
            
            # Number of rounds input
            rounds = st.number_input(
                f'Number of Rounds for {category}',
                min_value=1,
                max_value=max_allowed_rounds,
                value=min(saved_settings['rounds'], max_allowed_rounds),
                key=f'rounds_{category}',
                on_change=on_rounds_change,
                args=(category,)
            )
            
            # Show message if rounds are restricted
            if max_allowed_rounds < 4:
                st.info(message)
            
            # Cutoff input
            cutoff = st.text_input(
                f'Cutoff for {category} (MM:SS format, e.g., 2:00)',
                value=saved_settings['cutoff'],
                key=f'cutoff_{category}',
                on_change=on_cutoff_change,
                args=(category,)
            )
            
            # Add advancement settings
            current_competitors = initial_competitors
            for round_num in range(1, rounds):
                if round_num == rounds - 1 and rounds > 1:
                    # Final size input for the last round
                    max_final_size = math.floor(current_competitors * 0.75)
                    default_final_size = min(8, max_final_size)
                    
                    final_size = st.number_input(
                        f'Final Round Size (competitors)',
                        min_value=2,
                        max_value=max_final_size,
                        value=min(saved_settings.get('final_size', default_final_size), max_final_size),
                        key=f'final_size_{category}',
                        on_change=on_final_size_change,
                        args=(category,),
                        help=f"Maximum allowed: {max_final_size} competitors (75% of previous round)"
                    )
                else:
                    # Percentage input for non-final rounds
                    advance_key = f'advance_r{round_num}'
                    default_advance = 75
                    advance_percent = st.number_input(
                        f'Advance to Round {round_num + 1} (%)',
                        min_value=25,
                        max_value=75,
                        value=saved_settings.get(advance_key, default_advance),
                        key=f'{advance_key}_{category}',
                        on_change=on_advance_change,
                        args=(category, advance_key),
                        help="Between 25% and 75% of competitors must advance"
                    )
                    current_competitors = round_up_to_5(current_competitors * (advance_percent / 100))
                    
                    if round_num < rounds - 2:  # Show estimated competitors for next round if it's not the final
                        st.info(f"Approximately {current_competitors} competitors will advance")
    
    # Display results if categories are selected
    if selected_categories:
        # Display estimated competitors table
        st.subheader('Estimated Competitors per Category')
        estimates_df = calculate_estimated_competitors(
            number_of_competitors,
            selected_categories,
            st.session_state.rounds_cutoffs
        )
        st.dataframe(estimates_df)
        
        # Generate and display schedule
        st.subheader('Competition Schedule')
        schedule_df, warnings = schedule_competition(
            estimates_df, 
            num_days, 
            day_schedules, 
            main_event,
            st.session_state.rounds_cutoffs
        )
        
        # Display warnings if any
        if warnings:
            with st.expander("Scheduling Recommendations", expanded=True):
                for warning in warnings:
                    st.warning(warning)
        
        # Display the schedule in the enhanced format
        display_schedule(schedule_df)
        
        # Show raw schedule data in an expander
        with st.expander("View Raw Schedule Data"):
            st.dataframe(schedule_df)