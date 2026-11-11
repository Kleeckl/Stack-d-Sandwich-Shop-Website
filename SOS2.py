from os import path
from platform import node
import streamlit as st
from datetime import datetime
from xml.dom import Node
import pyrebase
from pathlib import Path

projectid = "fill in"
dburl = "https://ctdproj-6e4fd-default-rtdb.asia-southeast1.firebasedatabase.app/"
authdomain = projectid + ".firebaseapp.com"
storageBucket = projectid + ".appspot.com"
apikey = "AIzaSyBDRT3EGP-G7C-NoE6_1f13LE2VXPFVVGM"
email = "dummy@test.com"
password = "testing"

config = {
    "apiKey": apikey,
    "authDomain": authdomain,
    "databaseURL": dburl, 
    "storageBucket": storageBucket
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(email, password)
db = firebase.database()
user = auth.refresh(user['refreshToken']) #initialization for firebase RT DB

def up_dat(key, value):  # Function for updating loyalty points
    ID = key
    old_data = dl_dat(ID)  # Get data from database
    
    # Handle different data types returned from Firebase
    if old_data is None:
        old_lp = 0
    elif isinstance(old_data, dict):
        old_lp = old_data.get('points', 0)
    else:
        # If it's already a number
        old_lp = int(old_data)
    
    new_lp = old_lp + st.session_state.points
    
    # Store as simple integer to flatten structure
    node = db.child(ID).set(new_lp, user['idToken'])

def check_dat(key):
    node = db.child(key).get(user['idToken'])
    return (node.val() is not None)
    
def dl_dat(key): #Function for checking the amount of loyalty points the member has
    node = db.child(key).get(user['idToken']) #get the value from the DB
    return node.val() #return just the number of loyalty points





# For Cart Persistence
if 'cart_items' not in st.session_state:
    st.session_state.cart_items = []

# For Membership ID tracking
if 'ID' not in st.session_state:
    st.session_state.ID =""

# For loyalty point tracking:
if 'points' not in st.session_state:
    st.session_state.points = 0
# Page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'ordering'

if 'order_confirmed' not in st.session_state:
    st.session_state.order_confirmed = False

if 'confirmed_total' not in st.session_state:
    st.session_state.confirmed_total = 0.0

# Pricing dictionaries (for all items)
Bread_p = {"W": 1.00, "WM": 1.20, "PO": 1.40, "IH": 1.60}
Mains_p = {"EM": 2.00, "C": 3.00, "TUR": 3.20, "TUN": 2.80, "P": 2.60}
Addons_p = {"CH": 0.80, "CO": 1.50, "BB": 2.20, "CHI": 1.80, "D": 1.70}
Veg = {"L": "Lettuce", "T": "Tomatoes", "ON": "Onion", "C": "Cucumber", "OL": "Olives", "P": "Pickles"}
Meal_p = {"A": 1.30, "B": 2.70, "D": 2.50}

# Create display dictionaries for user since they don't know the shorthand names
BREADS = {"White": 1.00, "Wholemeal": 1.20, "Parmesan Oregano": 1.40, "Italian Herbs": 1.60}
MAINS = {"Egg Mayo": 2.00, "Chicken": 3.00, "Turkey": 3.20, "Tuna": 2.80, "Paneer": 2.60}
CHEESE_ADDON = 0.80
VEG_OPTIONS = ["Lettuce", "Tomatoes", "Onion", "Cucumber", "Olives", "Pickles"]
SAUCES = {"Mayo": 0.30, "Mustard": 0.30, "BBQ": 0.30, "Ranch": 0.30, "Sweet Chili": 0.30, "Garlic Aioli": 0.30}
OTHER_ADDONS = {"Cookie": 1.50, "Banana bread": 2.20, "Chips": 1.80, "Drink": 1.70}

# Bundle definitions with the discounts
BUNDLES = {"Solo": {"items": [], "discount": 0.00}, "Meal A": {"items": ["Drink"], "discount": 0.40, "price": 1.30}, "Meal B": {"items": ["Chips", "Drink"], "discount": 0.80, "price": 2.70}, "Deluxe": {"items": ["Drink", "Cookie"], "discount": 0.70, "price": 2.50}}

# Helper function to format bundle display
def format_bundle_display(bundle_name):
    bundle = BUNDLES[bundle_name]
    if bundle['discount'] > 0:
        return f"{bundle_name} - {bundle['items']} (Save ${bundle['discount']:.2f})"
    else:
        return bundle_name

# Helper function to format bread display
def format_bread_display(bread_name):
    return f"{bread_name} - ${BREADS[bread_name]:.2f}"

# Helper function to format main display
def format_main_display(main_name):
    return f"{main_name} - ${MAINS[main_name]:.2f}"

# Helper function to format addon display
def format_addon_display(addon_name):
    return f"{addon_name} - ${OTHER_ADDONS[addon_name]:.2f}"

# Tax and service rates
GST_RATE = 0.10  # 10% GST
SERVICE_CHARGE_RATE = 0.05  # 5% service charge
STUDENT_DISCOUNT_RATE = 0.10  # 10% student discount

# Helper functions to convert between codes and display names
def get_bread_code(display_name):
    bread_mapping = {
        "White": "W",
        "Wholemeal": "WM", 
        "Parmesan Oregano": "PO",
        "Italian Herbs": "IH"
    }
    return bread_mapping.get(display_name)

def get_main_code(display_name):
    main_mapping = {
        "Egg Mayo": "EM",
        "Chicken": "C",
        "Turkey": "TUR", 
        "Tuna": "TUN",
        "Paneer": "P"
    }
    return main_mapping.get(display_name)

def get_addon_code(display_name):
    addon_mapping = {
        "Cookie": "CO",
        "Banana bread": "BB",
        "Chips": "CHI",
        "Drink": "D"
    }
    return addon_mapping.get(display_name)

def get_veg_code(display_name):
    veg_mapping = {
        "Lettuce": "L",
        "Tomatoes": "T",
        "Onion": "ON",
        "Cucumber": "C",
        "Olives": "OL",
        "Pickles": "P"
    }
    return veg_mapping.get(display_name)

# Calculate prices of all the items selected
def calculate_sandwich_subtotal(bread, main, cheese, sauces):
    subtotal = 0.0
    
    if bread:
        bread_code = get_bread_code(bread)
        subtotal += Bread_p[bread_code]
    if main:
        main_code = get_main_code(main)
        subtotal += Mains_p[main_code]
    if cheese:
        subtotal += Addons_p["CH"]  # Cheese addon
    
    # Sauce = 30 cents each after first 2 free
    sauce_count = len(sauces)
    if sauce_count > 2:
        extra_sauces = sauce_count - 2
        subtotal += extra_sauces * 0.30
    
    return subtotal

def calculate_bundle_total(sandwich_subtotal, bundle_type, selected_addons):
    bundle = BUNDLES[bundle_type]
    
    if bundle_type == "Solo":
        # Solo meal
        bundle_total = sandwich_subtotal
        for addon in selected_addons:
            addon_code = get_addon_code(addon)
            if addon_code:
                bundle_total += Addons_p[addon_code]
    else:
        # Bundle meals
        meal_code_map = {"Meal A": "A", "Meal B": "B", "Deluxe": "D"}
        meal_code = meal_code_map[bundle_type]
        bundle_total = sandwich_subtotal + Meal_p[meal_code]
        
        # Add any additional selected add-ons
        for addon in selected_addons:
            if addon not in bundle["items"]:
                addon_code = get_addon_code(addon)
                if addon_code:
                    bundle_total += Addons_p[addon_code]
    
    return max(bundle_total, 0)  # Ensure no negative totals

def apply_discounts_and_charges(subtotal, is_student, one_off, two_off, apply_service_charge):
    total = subtotal
    breakdown = {}
    
    # Student discount
    if is_student:
        student_discount = total * STUDENT_DISCOUNT_RATE
        total -= student_discount
        breakdown["Student Discount (10%)"] = -student_discount
    
    # Service charge
    if apply_service_charge:
        service_charge = total * SERVICE_CHARGE_RATE
        total += service_charge
        breakdown["Service Charge (5%)"] = service_charge

    # $1 off membership discount
    if one_off:
        total -= 1
        breakdown["1 Dollar Off Membership Discount"] = -1

    # $2 off membership discount
    if two_off:
        total -= 2
        breakdown["2 Dollars Off Membership Discount"] = -2

    # GST
    gst = total * GST_RATE
    total += gst
    breakdown["GST (10%)"] = gst
    
    return total, breakdown

def ordering_page():
    one_off = None
    two_off = None
    st.title("Welcome to Stack'd!!!")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Build Your Sandwich")
        
        # Bread selection
        st.subheader("1. Choose Your Bread")
        bread = st.selectbox(
            "Select bread type:",
            options=list(BREADS.keys()),
            format_func=format_bread_display
        )
        
        # Main selection
        st.subheader("2. Choose Your Main")
        main = st.selectbox(
            "Select main filling:",
            options=list(MAINS.keys()),
            format_func=format_main_display
        )
        
        # Cheese add-on
        st.subheader("3. Cheese Add-on")
        cheese_options = ["No Cheese", f"Add Cheese (+${CHEESE_ADDON:.2f})"]
        cheese_choice = st.radio("Choose cheese option:", cheese_options)
        cheese = cheese_choice != "No Cheese"  # True if cheese is selected
        
        # Vegetables (free)
        st.subheader("4. Fresh Vegetables (Free)")
        vegetables = st.multiselect("Select vegetables:", VEG_OPTIONS)
        
        # Sauces (first 2 free)
        st.subheader("5. Sauces (First 2 Free)")
        sauces = st.multiselect(
            "Select sauces:",
            options=list(SAUCES.keys()),
            help="First 2 sauces are free, additional sauces cost $0.30 each"
        )
        
        # Bundle selection
        st.subheader("6. Meal Bundles")
        bundle_type = st.radio(
            "Choose your meal type:",
            options=list(BUNDLES.keys()),
            format_func=format_bundle_display
        )
        
        # Additional add-ons
        st.subheader("7. Additional Add-ons")
        bundle_items = BUNDLES[bundle_type]["items"]
        available_addons = [item for item in OTHER_ADDONS.keys() if item not in bundle_items]
        
        if bundle_items:
            st.info(f"Bundle includes: {', '.join(bundle_items)}")
        
        additional_addons = st.multiselect(
            "Select additional items:",
            options=available_addons,
            format_func=format_addon_display
        )
        
        # Customer options
        st.subheader("8. Customer Options")
        col_a, col_b = st.columns(2)
        
        with col_a:
            is_student = st.checkbox("Student Discount (10% off)")
        with col_b:
            apply_service_charge = st.checkbox("Dine-in (5% service charge)")


        # Membership Discounts/Loyalty Point Redemption
        st.subheader("9. Member Deals!")
        def update_member_id():
            st.session_state.ID = mID
        mID = str(st.text_input("Enter your 8-digit Membership ID:", value=st.session_state.ID, key = "member_ID", on_change=update_member_id, max_chars=8, placeholder = "Membership ID", icon = "💳"))
        mem_stat = check_dat(mID)
        if mID:
            if (mem_stat):
                loy_pts = int(dl_dat(mID))
                st.write(f"Welcome Member {mID}!")
                loy_string = f"You have {loy_pts} Stack Points!"
                st.write(loy_string)
                col_a, col_b = st.columns(2)
                if loy_pts >= 10:
                    with col_a:
                        one_off= st.checkbox("$1 off for 10 Stack Points!", value=False)
                        if one_off:
                            st.session_state.points =-10
                if loy_pts >=20:
                    with col_b:
                        two_off= st.checkbox("$2 off for 20 Stack Points!", value = False)
                        if two_off:
                            st.session_state.points =-20
            else:
                st.write("Invalid Membership ID!")

    
    with col2:
        st.image(Path("logo.png"))
        st.header("Order Summary")
        
        # Calculate sandwich subtotal
        sandwich_subtotal = calculate_sandwich_subtotal(bread, main, cheese, sauces)
        
        # Calculate bundle total
        bundle_total = calculate_bundle_total(sandwich_subtotal, bundle_type, additional_addons)
        
        # Apply discounts and charges
        final_total, breakdown = apply_discounts_and_charges(
            bundle_total, is_student, one_off, two_off, apply_service_charge
        )
        
        # Quick summary
        st.subheader("Quick Summary")
        st.write(f"**Sandwich**: {bread} with {main}")
        if cheese:
            st.write(f"**Cheese**: Added (+${CHEESE_ADDON:.2f})")
        if vegetables:
            st.write(f"**Vegetables**: {', '.join(vegetables)}")
        if sauces:
            st.write(f"**Sauces**: {', '.join(sauces)}")
        st.write(f"**Bundle**: {bundle_type}")
        if additional_addons:
            st.write(f"**Add-ons**: {', '.join(additional_addons)}")
        
        st.markdown("---")
        st.write(f"## **TOTAL: ${final_total:.2f}**")
        
        # Add to cart button
        if st.button("🛒 Add to Cart", type="primary"):
            order_item = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "bread": bread,
                "main": main,
                "cheese": cheese,
                "vegetables": vegetables,
                "sauces": sauces,
                "bundle": bundle_type,
                "additional_addons": additional_addons,
                "is_student": is_student,
                "one_off": one_off,
                "two_off": two_off,
                "service_charge": apply_service_charge,
                "total": final_total
            }
            st.session_state.cart_items.append(order_item)
            st.success("Item added to cart!")
        
        # Display cart
        if st.session_state.cart_items:
            st.subheader("🛒 Current Cart")
            cart_total = 0
            
            # Display each item with remove button
            for i, item in enumerate(st.session_state.cart_items):
                col_item, col_remove = st.columns([3, 1])
                
                with col_item:
                    st.write(f"{i+1}. {item['main']} on {item['bread']} - ${item['total']:.2f}")
                
                with col_remove:
                    if st.button("❌", key=f"remove_{i}", help="Remove this item"):
                        st.session_state.cart_items.pop(i)
                        st.rerun()
                
                cart_total += item['total']
            
            st.write(f"**Cart Total: ${cart_total:.2f}**")
            
            # Checkout button
            if st.button("📋 Checkout & View Bill", type="primary"):
                st.session_state.current_page = 'checkout'
                st.rerun()

def checkout_page():
    st.title("📋 Checkout & Itemized Bill")
    mID = st.session_state.ID
    # Check if order was just confirmed
    if st.session_state.order_confirmed:
        st.success(f" Order confirmed! Total: ${st.session_state.confirmed_total:.2f}")
        points = st.session_state.points
        st.write(f"Member {mID} have gained/lost {points} Stack Points!")
        # Center the button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("📦 Start New Order", type="primary"):
                st.session_state.current_page = 'ordering'
                st.session_state.order_confirmed = False
                st.session_state.confirmed_total = 0.0
                st.rerun()
        
        st.markdown("---")
        st.info("Thank you for your order! You can start a new order when ready.")
        return
    
    # Back button
    if st.button("← Back to Ordering", type="secondary"):
        st.session_state.current_page = 'ordering'
        st.rerun()
    
    if not st.session_state.cart_items:
        st.warning("Your cart is empty. Please add items before checkout.")
        return
    
    st.markdown("---")
    
    total_order_cost = 0
    
    for i, item in enumerate(st.session_state.cart_items):
        st.subheader(f"Item {i+1}: {item['main']} Sandwich")
        
        sandwich_subtotal = calculate_sandwich_subtotal(
            item['bread'], item['main'], item['cheese'], item['sauces']
        )
        bundle_total = calculate_bundle_total(
            sandwich_subtotal, item['bundle'], item['additional_addons']
        )
        final_total, breakdown = apply_discounts_and_charges(
            bundle_total, item['is_student'], item['one_off'], item['two_off'], item['service_charge']
        )
        
        # Detailed breakdown
        col_details, col_remove = st.columns([4, 1])
        
        with col_details:
            st.write("**Sandwich Components:**")
            bread_code = get_bread_code(item['bread'])
            main_code = get_main_code(item['main'])
            
            st.write(f"• {item['bread']} ({bread_code}): ${Bread_p[bread_code]:.2f}")
            st.write(f"• {item['main']} ({main_code}): ${Mains_p[main_code]:.2f}")
            
            if item['cheese']:
                st.write(f"• Cheese (CH): ${Addons_p['CH']:.2f}")
            
            if item['vegetables']:
                st.write(f"• Vegetables: {', '.join(item['vegetables'])} (Free)")
            
            if item['sauces']:
                sauce_cost = max(0, len(item['sauces']) - 2) * 0.30
                if sauce_cost > 0:
                    st.write(f"• Sauces: {', '.join(item['sauces'])} (2 free + ${sauce_cost:.2f})")
                else:
                    st.write(f"• Sauces: {', '.join(item['sauces'])} (Free)")
            
            st.write(f"**Sandwich Subtotal: ${sandwich_subtotal:.2f}**")
            
            # Bundle items
            if item['bundle'] != "Solo":
                st.write("**Bundle Items:**")
                meal_code_map = {"Meal A": "A", "Meal B": "B", "Deluxe": "D"}
                meal_code = meal_code_map[item['bundle']]
                st.write(f"• {item['bundle']} ({meal_code}): ${Meal_p[meal_code]:.2f}")
                
                for bundle_item in BUNDLES[item['bundle']]["items"]:
                    addon_code = get_addon_code(bundle_item)
                    st.write(f"  - Includes {bundle_item} ({addon_code})")
            
            # Additional add-ons
            if item['additional_addons']:
                st.write("**Additional Add-ons:**")
                for addon in item['additional_addons']:
                    addon_code = get_addon_code(addon)
                    st.write(f"• {addon} ({addon_code}): ${Addons_p[addon_code]:.2f}")
            
            st.write(f"**Subtotal: ${bundle_total:.2f}**")
            
            # Discounts and charges breakdown
            if breakdown:
                st.write("**Adjustments:**")
                for description, amount in breakdown.items():
                    if amount < 0:
                        st.write(f"• {description}: -${abs(amount):.2f}")
                    else:
                        st.write(f"• {description}: +${amount:.2f}")
            
            st.write(f"**Item Total: ${final_total:.2f}**")
        
        with col_remove:
            if st.button("❌ Remove", key=f"checkout_remove_{i}", help="Remove this item"):
                st.session_state.cart_items.pop(i)
                st.rerun()
        
        total_order_cost += final_total
        st.markdown("---")
    
    # Final order total
    st.write(f"# **FINAL ORDER TOTAL: ${total_order_cost:.2f}**")
    
    # Final checkout button
    col_back, col_confirm = st.columns(2)
    
    with col_back:
        if st.button("← Continue Shopping"):
            st.session_state.current_page = 'ordering'
            st.rerun()
    
    with col_confirm:
        if st.button("✅ Confirm Order", type="primary"):
            st.session_state.order_confirmed = True
            st.session_state.confirmed_total = total_order_cost
            st.session_state.points += int((total_order_cost * 2))
            mID = st.session_state.ID
            if mID and check_dat(mID):
                points = st.session_state.points
                up_dat(mID, st.session_state.points)
            elif mID and not check_dat(mID):
                st.warning("Invalid membership ID. Points not updated.")
            else:
                st.info("No membership ID provided. Points not saved.")
            st.session_state.cart_items = [] 
            st.rerun()

def main():
    # Page Navigation
    if st.session_state.current_page == 'ordering':
        ordering_page()
    elif st.session_state.current_page == 'checkout':
        checkout_page()

if __name__ == "__main__":
    main()