var get_css_color = function(tankcolor) {
    var sc = 255.0/90;
    return 'rgb('+(tankcolor[0]*sc)+','+(tankcolor[1]*sc)+','+(tankcolor[2]*sc)+')';
}

var running = false;
var stop_on_turn = false;

function handle_stat(id, stat_json){
	st = JSON.parse(stat_json);
	if(id != 'user') return;
	$('#health_status').text(st.hp.toFixed(2) + ' / ' + st.max_hp);
	$('#health_bar_status').css('width',(100*st.hp/st.max_hp).toFixed(2)+'%');
	$('#ammo_status').text(st.ammo);
	$('#score_status').text(st.ammo);
	if(st.alive){
		$('#statusbox .bcell').css('fill', get_css_color(st.color));
		$('#respawn').addClass('disabled');
	} else {
		$('#statusbox .bcell').css('fill', '#aaa')
		$('#respawn').removeClass('disabled');
	}
	if(stop_on_turn){
		running = false;
		$('#pause').addClass('disabled');
		$('#step').removeClass('disabled');
		$('#run').removeClass('disabled');
	}
}
function handle_log(id, logs){
	log_list = JSON.parse(String(logs));
	// console.log("Got logs", id, log_list);
	if(id != 'user') return;
	for (var i = 0; i < log_list.length; i++) {
		$('<span>').text(log_list[i]).appendTo($('#logoutput'));
	};
}
function handle_leaderboard(leaderboard){
	// console.log("Got leaderboard", leaderboard);
}
function update_board(board){
	console.log("Got board");
	var COLORS = ['rgb(100,100,200)', 'rgb(200,100,100)', 'rgb(100,200,100)', 'rgb(200,200,100)', 'rgb(200,100,200)', 'rgb(100,200,200)', 'rgb(100,60,200)', 'rgb(60,100,200)', 'rgb(200,60,100)', 'rgb(60,100,200)', 'rgb(0,0,0)', 'rgb(120, 120, 120)', 'rgb(0,0,200)', 'rgb(200,0,0)', 'rgb(0,0,0)', 'rgb(0,200,0)']
	if(ctx){
		ctx.clearRect(0,0,640,640);
		for (var r = 0; r < board.length; r++) {
			var row = board[r];
			for (var c = 0; c < row.length; c++) {
				var cell = row[c];
				ctx.fillStyle = COLORS[cell];
				ctx.fillRect(r*10+2,c*10+2,6,6);
			};
		};
	}
}

var command_queue = [];
function clearQueue(){
	res = Promise.resolve(true);
	for (var i = 0; i < command_queue.length; i++) {
		function closure_run(cmd){
			return res.then(function(){
				console.log("inserting command", cmd);
				return pypyjs.exec(cmd);
			});
		}
		res = closure_run(command_queue[i]);
	};
	command_queue = [];
	return res;
}

function doturn(){
	return clearQueue().then(function(){
		return pypyjs.exec('runner.next()');
	});
}

function doturn_cts(){
	doturn().then(function(){
		if(running)
			window.requestAnimationFrame(doturn_cts);
		else
			force_drawboard();
	})
}

function start_doturn_cts(step){
	if(running) return;
	stop_on_turn = step;
	running = true;
	pypyjs.exec('game.fix_time_after_pause()').then(function(){
		doturn_cts();
	})
}
function stop_doturn_cts(){
	running = false;
}

function force_drawboard(){
	return clearQueue().then(function(){
		return pypyjs.exec('game.force_draw()');
	})
}

var basictank="class TankAI:\n    def init(self,init_state):\n        pass\n    def takeTurn(self,state):\n        print \"hi\"\n        return [[1, 1], True, [0, 1]]"
pypyjs.ready().then(function() {
	// this callback is fired when the interpreter is ready for use.
	console.log("ready!");
	pypyjs.set("enemy_tank_code",enemycode);
	pypyjs.set("user_tank_code",usercode);
	pypyjs.exec("import game; game.setup_simulation();" + 
				"game.store_ais({'../data/user.py': user_tank_code});" +
				"game.spawn_ai('user');" +
				"runner = game.turn_generator()")
		.then(function(){
			enemy_ct = 0;
			$("#loading").hide();
			force_drawboard();
			$('#pause').removeClass('disabled');
			start_doturn_cts(false);
		});
});
var canvas, ctx, enemy_ct;

$(function(){
	canvas = $('#board')[0];
	ctx = canvas.getContext('2d');
	$('#spawn').click(function(){
		var enemy_id = "enemy_"+enemy_ct;
		command_queue.push("game.store_ais({'../data/" + enemy_id + ".py': enemy_tank_code});" +
			"game.spawn_ai('"+ enemy_id +"');");
		enemy_ct++;
	});
	$('#respawn').click(function(){
		command_queue.push("game.spawn_ai('user');");
	});

	$('#clear').click(function(){
		$('#logoutput').empty();
	});

	$('#run').click(function(){
		if($('#run').hasClass('disabled')) return;
		start_doturn_cts(false);
		$('#run').addClass('disabled');
		$('#step').addClass('disabled');
		$('#pause').removeClass('disabled');
	});
	$('#pause').click(function(){
		if($('#pause').hasClass('disabled')) return;
		stop_doturn_cts();
		$('#pause').addClass('disabled');
		$('#step').removeClass('disabled');
		$('#run').removeClass('disabled');
	});
	$('#step').click(function(){
		if($('#step').hasClass('disabled')) return;
		start_doturn_cts(true);
		$('#step').addClass('disabled');
		$('#run').addClass('disabled');
		$('#pause').addClass('disabled');
	});
	$('#ffwdspeed').click(function(){
		if($('#ffwdspeed').hasClass('disabled')) return;
		command_queue.push("game.the_game.fast_forward = True;");
		$('#ffwdspeed').addClass('disabled');
		$('#normspeed').removeClass('disabled');
	});
	$('#normspeed').click(function(){
		if($('#normspeed').hasClass('disabled')) return;
		command_queue.push("game.the_game.fast_forward = False;");
		$('#normspeed').addClass('disabled');
		$('#ffwdspeed').removeClass('disabled');
	});
})
