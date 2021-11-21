import pyrebase
firebaseConfig = {

  "apiKey": "AIzaSyBV8LBeKr0RhecjC81_ohqu4BggEqh1Nrw",

  "authDomain": "submissiontool-2f18a.firebaseapp.com",

  "projectId": "submissiontool-2f18a",

  "storageBucket": "submissiontool-2f18a.appspot.com",

  "messagingSenderId": "155602755028",

  "appId": "1:155602755028:web:0cfb3d2c8a3b6ce0c04a41",

  "databaseURL": "https://submissiontool-2f18a-default-rtdb.firebaseio.com",

  "measurementId": "G-79SST9VTCL"

}
firebase = pyrebase.initialize_app(firebaseConfig)