from flask import Flask, render_template, request, jsonify, session
import random
import time
import smtplib

app = Flask(__name__)
app.secret_key = "change_this_secret_key_123"

# ================= SETTINGS =================
OTP_EXPIRY_SECONDS = 120
OTP_LENGTH = 6

# 👉 PUT YOUR EMAIL DETAILS HERE
EMAIL_ADDRESS = "gourigiddale26@gmail.com"
EMAIL_PASSWORD = "nsxfqjgmdmkxiwva"

# Store OTP in memory
otp_store = {}

# ================= OTP GENERATOR =================
def generate_otp():
    return "".join([str(random.randint(0, 9)) for _ in range(OTP_LENGTH)])


# ================= SEND EMAIL =================
def send_email_otp(receiver_email, otp):
    try:
        subject = "Your OTP Code"
        body = f"Your OTP is: {otp}\nThis OTP will expire in {OTP_EXPIRY_SECONDS} seconds."

        message = f"Subject: {subject}\n\n{body}"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, receiver_email, message)
        server.quit()

        print(f"[EMAIL SENT] OTP sent to {receiver_email}")

        return True
    except Exception as e:
        print("Email Error:", e)
        return False


# ================= ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")


# ---------- SEND OTP ----------
@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"success": False, "message": "Email required"}), 400

    otp = generate_otp()

    # Store OTP
    otp_store[email] = {
        "otp": otp,
        "expires_at": time.time() + OTP_EXPIRY_SECONDS
    }

    # Send email
    email_sent = send_email_otp(email, otp)

    if not email_sent:
        return jsonify({
            "success": False,
            "message": "Failed to send email. Check SMTP settings."
        }), 500

    return jsonify({
        "success": True,
        "message": "OTP sent to your email!"
    })


# ---------- VERIFY OTP ----------
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()

    record = otp_store.get(email)

    if not record:
        return jsonify({"success": False, "message": "No OTP found"}), 400

    if time.time() > record["expires_at"]:
        del otp_store[email]
        return jsonify({"success": False, "message": "OTP expired"}), 400

    if otp != record["otp"]:
        return jsonify({"success": False, "message": "Invalid OTP"}), 400

    # Success
    del otp_store[email]
    session["user"] = email

    return jsonify({
        "success": True,
        "message": "Login successful!"
    })


# ---------- LOGOUT ----------
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


# ================= RUN =================
if __name__ == "__main__":
    print("\n🚀 Flask OTP Server Running...")
    print("👉 Open: http://127.0.0.1:5000\n")
    app.run(debug=True)