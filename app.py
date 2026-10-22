import streamlit as st
import pandas as pd
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

# --- 2. Session State for Daily Limit (100 Dabbes Lock) ---
if "total_booked_today" not in st.session_state:
    st.session_state.total_booked_today = 0  # Aaj ke total booked dabbes

DAILY_LIMIT = 100
remaining_dabbes = DAILY_LIMIT - st.session_state.total_booked_today

# --- 3. Sidebar Student Registration ---
st.sidebar.header("📋 Student Registration")
name = st.sidebar.text_input("Name")
phone = st.sidebar.text_input("Mobile Number")
address = st.sidebar.text_area("Hostel / Room Address")

map_location = st.sidebar.text_input("Google Maps Location Link (Optional)", placeholder="Google Maps ka share link paste karein")

st.sidebar.write("---")
st.sidebar.info(f"📊 **Aaj ki Limit:** {DAILY_LIMIT} Dabbes\n\n🔥 **Bache hue Dabbe:** {remaining_dabbes}")

# --- 4. Today's Menu Display & Limit Check ---
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

    # --- 5. Cart & Dynamic UPI QR Code Payment ---
    st.header("🛒 Cart & Payment")

    if st.session_state.cart:
        total = sum(i["price"] for i in st.session_state.cart)
        for i in st.session_state.cart:
            st.write(f"- {i['name']} : ₹{i['price']}")

        st.write(f"### **Total Amount: ₹{total}**")
        
        st.write("---")
        st.subheader("💳 Online Payment (UPI / QR Code)")
        st.info("💡 Niche diye gaye UPI ID ya QR Code par PhonePe / Google Pay / Paytm se payment karein:")

        # ⚠️ Yahan apni asli UPI ID daalein (Jaise: 9876543210@paytm ya yourname@okaxis)
        UPI_ID = "7385804669@kotakbank"

        st.markdown(f"👉 **UPI ID:** `{UPI_ID}`")

        # Dynamic QR Code URL (It automatically sets the total bill amount)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=upi://pay?pa={UPI_ID}&pn=Student%20Dabba%20Express&am={total}&cu=INR"
        
        st.image(qr_url, caption=f"Scan to Pay ₹{total} via Google Pay / PhonePe / Paytm", width=200)

        st.write("---")
        st.subheader("📲 Confirm Your Order")
        utr_number = st.text_input("Payment hone ke baad UTR / Transaction ID yahan daalein:")

        if st.button("Confirm Order 🚀"):
            if not name or not phone or not address:
                st.error("Kripya pehle Sidebar mein apna Naam, Mobile Number aur Address bharein!")
            elif not utr_number.strip():
                st.error("Kripya payment ka UTR / Transaction ID zaroor daalein!")
            else:
                st.balloons()
                st.session_state.total_booked_today += len(st.session_state.cart)
                
                # 🔔 Order Sound Effect
                st.components.v1.html("""
                    <audio autoplay>
                        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                    </audio>
                """, height=0)

                st.success(f"🎉 Shukriya {name}! Aapka order successfully confirm ho gaya hai.")
                st.info(f"📍 **Delivery Address:** {address}\n\n📞 **Phone:** {phone}\n💳 **UTR Number:** {utr_number}")

                # Cart khali karein
                st.session_state.cart = []
    else:
        st.info("Aapka cart khali hai. Menu se Dabba select karein!")
