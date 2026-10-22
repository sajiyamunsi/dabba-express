import streamlit as st
import pandas as pd
import razorpay
import streamlit.components.v1 as components

st.set_page_config(page_title="Student Dabba Express", page_icon="🍲")

st.title("🍲 Student Dabba Express")
st.subheader("Ghar jaisa khana, direct aapke room tak!")

# --- 1. Google Sheet Connection ---
SHEET_ID = "19frWZEJsRh0mPORoJbDj0ly86Hgcdr5a2KKpMlGRJZc"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

try:
    menu_data = pd.read_csv(url)
except Exception as e:
    st.error("Google Sheet connect nahi ho pa rahi. Sheet link check karein.")
    menu_data = None

# --- 2. Razorpay Client Setup ---
RAZORPAY_KEY_ID = "rzp_test_TqCNlYuU5wtn5j"
RAZORPAY_KEY_SECRET = "rg0NJUzr5yfDbkf86Q113Cev"

try:
    if "razorpay" in st.secrets:
        RAZORPAY_KEY_ID = st.secrets["razorpay"]["key_id"]
        RAZORPAY_KEY_SECRET = st.secrets["razorpay"]["key_secret"]
except Exception:
    pass

try:
    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
except Exception as e:
    client = None

# --- 3. Session State for Daily Limit (100 Dabbes Lock) ---
if "total_booked_today" not in st.session_state:
    st.session_state.total_booked_today = 0  # Aaj ke total booked dabbes

DAILY_LIMIT = 100
remaining_dabbes = DAILY_LIMIT - st.session_state.total_booked_today

# --- 4. Sidebar Student Registration ---
st.sidebar.header("📋 Student Registration")
name = st.sidebar.text_input("Name")
phone = st.sidebar.text_input("Mobile Number")
address = st.sidebar.text_area("Hostel / Room Address")

map_location = st.sidebar.text_input("Google Maps Location Link (Optional)", placeholder="Google Maps ka share link paste karein")

st.sidebar.write("---")
st.sidebar.info(f"📊 **Aaj ki Limit:** {DAILY_LIMIT} Dabbes\n\n🔥 **Bache hue Dabbe:** {remaining_dabbes}")

# --- 5. Today's Menu Display & Limit Check ---
st.write("---")
st.header("🍱 Today's Live Dabba Menu")

if st.session_state.total_booked_today >= DAILY_LIMIT:
    st.error("🚨 **Booking Locked!** Aaj ke sabhi 100 dabbe book ho chuke hain. Kal subah fir try karein!")
else:
    st.warning(f"⚠️ Dhyan dein: Aaj keval {remaining_dabbes} dabbe bache hain! 100 poore hote hi order lock ho jayega.")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    if menu_data is not None and not menu_data.empty:
        for index, row in menu_data.iterrows():
            item_name = row.get("Item_Name", "Dabba")
            price = row.get("Price", 0)
            desc = row.get("Description", "")
            img_url = row.get("Image_URL", "")

            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                if pd.notna(img_url) and str(img_url).startswith("http"):
                    st.image(img_url, width=100)
                else:
                    st.write("🍲")

            with col2:
                st.subheader(item_name)
                st.write(desc)
                st.write(f"**Price:** ₹{price}")

            with col3:
                if st.button("Add +", key=f"btn_{index}"):
                    st.session_state.cart.append({"name": item_name, "price": float(price)})
                    st.toast(f"{item_name} Cart mein add ho gaya!")

            st.write("---")

    # --- 6. Cart & Razorpay Secure Payment ---
    st.header("🛒 Cart & Payment")

    if st.session_state.cart:
        total = sum(i["price"] for i in st.session_state.cart)
        for i in st.session_state.cart:
            st.write(f"- {i['name']} : ₹{i['price']}")

        st.write(f"### **Total Amount: ₹{total}**")

        if st.button("Pay Now with Razorpay 💳"):
            if not name or not phone or not address:
                st.error("Kripya pehle Sidebar mein apna Naam, Mobile Number aur Address bharein!")
            elif client is None:
                st.error("Razorpay Client setup nahi ho paya.")
            else:
                try:
                    amount_in_paise = int(total * 100)
                    
                    order_data = {
                        "amount": amount_in_paise,
                        "currency": "INR",
                        "receipt": f"order_{phone}",
                        "payment_capture": 1
                    }
                    order = client.order.create(data=order_data)
                    
                    st.session_state.total_booked_today += len(st.session_state.cart)
                    st.session_state.cart = []  # Cart khali kar denge
                    
                    st.success(f"🎉 Order Created Successfully! Order ID: {order['id']}")
                    
                    # 🔔 Order Received Ringtone Sound
                    st.components.v1.html("""
                        <audio autoplay>
                            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                        </audio>
                    """, height=0)
                    
                    # Razorpay Checkout Popup Button HTML using .format() to avoid syntax errors
                    razorpay_checkout_html = """
                    <!DOCTYPE html>
                    <html>
                    <body>
                        <button id="rzp-button1" style="background-color: #3399cc; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer;">Pay ₹{} Now</button>
                        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
                        <script>
                        var options = {{
                            "key": "{}",
                            "amount": "{}",
                            "currency": "INR",
                            "name": "Student Dabba Express",
                            "description": "Dabba Booking Payment",
                            "order_id": "{}",
                            "handler": function (response){{
                                alert("Payment Successful! Payment ID: " + response.razorpay_payment_id);
                            }},
                            "prefill": {{
                                "name": "{}",
                                "contact": "{}"
                            }},
                            "theme": {{
                                "color": "#3399cc"
                            }}
                        }};
                        var rzp1 = new Razorpay(options);
                        document.getElementById('rzp-button1').onclick = function(e){{
                            rzp1.open();
                            e.preventDefault();
                        }}
                        </script>
                    </body>
                    </html>
                    """.format(total, RAZORPAY_KEY_ID, amount_in_paise, order['id'], name, phone)

                    components.html(razorpay_checkout_html, height=600)
                    
                except Exception as err:
                    st.error(f"Payment order banane mein error aaya: {err}")
    else:
        st.info("Aapka cart khali hai. Menu se Dabba select karein!")
        
        # --- Customer Chat & Feedback Section ---
st.write("---")
st.header("💬 Customer Chat & Special Requests")
feedback_msg = st.text_area("Apna Message / Feedback likhein:")
if st.button("Send Message"):
    if feedback_msg.strip():
        st.success("Aapka message humein mil gaya hai! Hum jald hi aapse sampark karenge. Shukriya! 🙏")
    else:
        st.warning("Kripya pehle koi message likhein!")