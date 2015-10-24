var express = require('express');
var passport = require('passport');
var GoogleStrategy = require('passport-google-oauth').OAuth2Strategy;
var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/test');
var findOrCreate = require('mongoose-findorcreate');

var credentials = require('./credentials');

var app = express();

app.use(express.static('files'));
app.use(require('cookie-parser')());
app.use(require('body-parser').urlencoded({ extended: true }));
app.use(require('express-session')({ secret: 'keyboard cat', resave: true, saveUninitialized: true }));
app.use(passport.initialize());
app.use(passport.session());


var UserSchema = new mongoose.Schema({ profile_id: String, name: String });
UserSchema.plugin(findOrCreate);
UserSchema.methods.findById = function (profile_id, cb) {
  return this.model('User').find({ profile_id: profile_id }, cb);
}
var User = mongoose.model('User', UserSchema);

passport.use(new GoogleStrategy({
    clientID: credentials.GOOGLE_CONSUMER_KEY,
    clientSecret: credentials.GOOGLE_CONSUMER_SECRET,
    callbackURL: 'http://localhost:3000/auth/google/return',
    },
    function(accessToken, refreshToken, profile, done) {
        console.log(profile);
        User.findOrCreate({ profile_id: profile.id }, { name: profile.displayName }, function(err, user) {
            return done(err, user);
        });
    }
));

passport.serializeUser(function(user, done) {
  done(null, user.id);
});

passport.deserializeUser(function(id, done) {
  User.findById(id, function(err, user) {
    done(err, user);
  });
});


app.get('/', function (req, res) {
    if(req.user){
        res.send('You are ' + req.user.name);
    }else{
        res.send('Hello World!');
    }
});

app.get('/auth/google',
    passport.authenticate('google', {scope: 'openid profile email', failureFlash: true}));

app.get('/auth/google/return', 
    passport.authenticate('google', { failureRedirect: '/login' }),
    function(req, res) {
        // Successful authentication, redirect home.
        res.redirect('/');
    });

app.get('/logout', function(req, res){
    req.logout();
    res.redirect('/');
});

var server = app.listen(3000, function () {
    var host = server.address().address;
    var port = server.address().port;

    console.log('Example app listening at http://%s:%s', host, port);
});