var express = require('express');
var passport = require('passport');
var GoogleStrategy = require('passport-google-oauth').OAuth2Strategy;
var path = require('path');
var S = require('string');
var flash = require('connect-flash');
var fs = require('fs');
var child_process = require('child_process');
var Datastore = require('nedb');
var crypto = require('crypto');

var credentials = require('./credentials');
var config = require('./config');

var app = express();

var userdb = new Datastore({ filename: '../data/usrdb.db', autoload: true });

passport.use(new GoogleStrategy({
    clientID: credentials.GOOGLE_CONSUMER_KEY,
    clientSecret: credentials.GOOGLE_CONSUMER_SECRET,
    callbackURL: config.base_url + '/auth/google/return',
    },
    function(accessToken, refreshToken, profile, done) {
        console.log(profile);
        if(!S(profile.emails[0].value).endsWith('@g.hmc.edu')){
            return done(null, false, { message: 'You need to sign up with a HMC account!'});
        }

        userdb.findOne({ profile_id: profile.id }, function(err, doc){
            if(err)
                return done(err, null);
            if(doc) {
                return done(null, doc);
            } else {
                userdb.insert({
                    profile_id: profile.id,
                    name: profile.displayName,
                    email: profile.emails[0].value,
                    student_id_num_hashed: null,
                }, done);
            }
        });     
    }
));

passport.serializeUser(function(user, done) {
    done(null, user._id);
});

passport.deserializeUser(function(_id, done) {
    userdb.findOne({ _id: _id }, done);
});

var ensureUserLoggedIn = function (req, res, next) {
    if(!req.user){
        res.redirect('/auth/google');
    }else{
        next();
    }
}

var ensureUserSetUp = function (req, res, next) {
    if(!req.user.student_id_num_hashed){
        res.redirect('/account/setup');
    } else {
        next();
    }
};

var ensureUserNotSetUp = function (req, res, next) {
    if(req.user.student_id_num_hashed){
        res.redirect('/');
    } else {
        next();
    }
};

var prepareRender = function (req, res, next) {
    res.locals.errmessages = req.flash('error');
    if(req.user){
        res.locals.navbar = {
            '/':'Home',
            '/account/info':'Account',
            '/status':'Status',
            '/leaderboard':'Leaderboard',
            '/edit':'Edit Code',
        }
        res.locals.name = req.user.name;
    } else {
        res.locals.navbar = {
            '/':'Home',
            '/auth/google':'Login',
        }
        res.locals.name = "not logged in"
    }
    next();
};


app.use(express.static(path.join(__dirname, 'public')));
app.use(require('cookie-parser')());
app.use(require('body-parser').urlencoded({ extended: true }));
app.use(require('express-session')({ secret: 'safewithme', resave: true, saveUninitialized: true }));
app.use(passport.initialize());
app.use(passport.session());
app.use(flash());
app.use(prepareRender);

app.set('views', './views');
app.set('view engine', 'jade');

app.get('/', function (req, res) {
    // console.log(req.flash('error'));
    res.render('home', { title: 'Home'})
});

app.get('/auth/google',
    passport.authenticate('google', {scope: 'openid profile email', failureFlash: true}));

app.get('/auth/google/return',
    passport.authenticate('google', { failureRedirect: '/', failureFlash: true }),
    function(req, res) {
        // Successful authentication, redirect home.
        res.redirect('/account/info');
    });

app.get('/logout', function(req, res){
    req.logout();
    res.redirect('/');
});

app.get('/account/setup',
    ensureUserLoggedIn,
    ensureUserNotSetUp,
    function (req, res) {
        res.render('acct_setup')
    }
);
app.post('/account/setup',
    ensureUserLoggedIn,
    ensureUserNotSetUp,
    function (req, res) {
        if(/^\d{8}$/g.test(req.body.idnum)){
            userdb.findOne({ student_id_num_hashed: req.body.idnum }, function(err, doc){
                if(err){
                    console.log(err);
                    res.status(500).send("Bad!");
                    return
                }
                if(doc) {
                    // User with this id number already exists!
                    req.flash('error', 'Someone else already registered that ID number!');
                    res.redirect('/account/setup');
                } else {
                    var shasum = crypto.createHash('sha512');
                    shasum.update(req.body.idnum);
                    var hashed_idnum = shasum.digest('hex');
                    userdb.update({ _id: req.user._id }, {$set:{ student_id_num_hashed: hashed_idnum }},
                    function(err, numReplaced, newDoc){
                        if(err){
                            console.log(err);
                            res.status(500).send("Bad!");
                            return
                        }
                        req.user = newDoc;

                        // Copy default file
                        var default_file = '../game/ais/tank_template.py';
                        var aifile = '../data/' + hashed_idnum + '.py';
                        var content = fs.readFileSync(default_file);
                        fs.writeFileSync(aifile, content);

                        res.redirect('/account/info');
                    });
                }
            });
        } else {
            // Bad ID number
            res.redirect('/account/setup');
        }
    }
);

app.get('/account/info',
    ensureUserLoggedIn,
    ensureUserSetUp,
    function (req, res) {
        res.render('acct_info')
    }
);

var get_player_status = function(idnum, cb) {
    var statusfile = '../data/' + idnum + '_stat.json';
    fs.stat(statusfile, function (err, stat) {
        if (!err && stat.isFile()){
            fs.readFile(statusfile, function(err, data) {
                if(err) {
                    cb(err, null);
                } else {
                    cb(null, JSON.parse(data));
                }
            });
        } else {
            cb(null, null);
        }
    });
}

var get_player_log = function(idnum, cb) {
    var logfile = '../data/' + idnum + '_out.log';
    fs.stat(logfile, function (err, stat) {
        if (!err && stat.isFile()){
            fs.readFile(logfile, cb);
        } else {
            cb(null, "No log to show.");
        }
    });
}

app.get('/status',
    ensureUserLoggedIn,
    ensureUserSetUp,
    function (req, res) {
        get_player_status(req.user.student_id_num_hashed, function(err, status){
            if (err){
                console.log(err);
                res.status(500).send("Bad!");
                return
            }
            get_player_log(req.user.student_id_num_hashed, function(err, log){
                if (err){
                    console.log(err);
                    res.status(500).send("Bad!");
                    return
                }
                res.render('status', {stats: status, log:log});
            });
        });
    }
);

var get_aifile_contents = function(idnum, cb) {
    var aifile = '../data/' + idnum + '.py';
    fs.readFile(aifile, cb);
}

app.get('/edit',
    ensureUserLoggedIn,
    ensureUserSetUp,
    function (req, res) {
        get_aifile_contents(req.user.student_id_num_hashed, function(err, contents){
            if (err){
                console.log(err);
                res.status(500).send("Bad!");
                return
            }
            res.render('edit', {initialcontents: contents});
        });
    }
);
app.post('/edit',
    ensureUserLoggedIn,
    ensureUserSetUp,
    function (req, res) {
        var aifile = '../data/' + req.user.student_id_num_hashed + '.py';
        fs.writeFile(aifile, req.body.value);
        child_process.execFile('python',['../game/test-compile.py', aifile],{},function(err,stdout,stderr){
            if (err) throw err;
            res.send(stdout);
        });
    }
);

var get_leaderboard = function(cb) {
    var logfile = '../data/leaderboard.json';
    fs.readFile(logfile, function(err, data) {
        if(err) {
            cb(err, null);
        } else {
            cb(null, JSON.parse(data));
        }
    });
}

var get_id_to_name_map = function(ids, cb){
    var id_to_name_map = {};
    var num_left = ids.length;
    function do_find(cur_id){
        userdb.findOne({ student_id_num_hashed: cur_id }, function(err, doc){
            if(err){
                console.log(err);
                id_to_name_map[cur_id] = "Error finding!";
            } else if(doc) {
                id_to_name_map[cur_id] = doc.name;
            } else {
                id_to_name_map[cur_id] = cur_id + " (non-player tank)";
            }
            num_left--;
            if(num_left == 0){
                cb(id_to_name_map);
            }
        });
    }
    for (var i = 0; i < ids.length; i++) {
        do_find(ids[i]);
    };
}

app.get('/leaderboard',
    ensureUserLoggedIn,
    ensureUserSetUp,
    function (req, res) {
        get_leaderboard(function(err, leaderboard){
            if (err){
                console.log(err);
                res.status(500).send("Bad!");
                return
            }
            var ids = []
            for (var i = 0; i < leaderboard.length; i++) {
                ids[i] = leaderboard[i].id;
            };
            get_id_to_name_map(ids, function(map){
                res.render('leaderboard', {leaderboard:leaderboard, namemap:map})
            });
        });
    }
);

var server = app.listen(config.listen_port, function () {
    var host = server.address().address;
    var port = server.address().port;

    console.log('Example app listening at http://%s:%s', host, port);
});
