function handle_stat(id, stat_json){
	st = JSON.parse(stat_json);
	if(id != 'user') return;
	$('#health_status').text(st.hp.toFixed(2) + ' / ' + st.max_hp);
	$('#health_bar_status').css('width',(100*st.hp/st.max_hp).toFixed(2)+'%');
	$('#ammo_status').text(st.ammo);
	$('#score_status').text(st.ammo);
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
function doturn(){
	// console.log("turn!");
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
	return res.then(function(){
		pypyjs.exec('runner.next()');
	});
}
function doturn_cts(){
	doturn().then(function(){
		window.requestAnimationFrame(doturn_cts);
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
			doturn_cts();
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

	$('#clear').click(function(){
		$('#logoutput').empty();
	});
})
