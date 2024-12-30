import pyxel
import math
import random

def draw_text_with_border(x, y, s, col, bcol, font):
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx != 0 or dy != 0:
                pyxel.text(
                    x + dx,
                    y + dy,
                    s,
                    bcol,
                    font,
                )
    pyxel.text(x, y, s, col, font)

class App:
    def __init__(self):
        # ゲームウィンドウを初期化（幅256px、高さ256px）
        pyxel.init(256, 256, title="My Pyxel Game", capture_scale=1, capture_sec=0)
        
        # プレイヤーの初期状態を設定
        self.player_x = 0  # マップ上の位置
        self.player_y = 0
        self.player_size = 8
        self.player_speed = 2
        self.player_hp = 10  # プレイヤーの体力
        self.max_hp = 10     # 最大体力
        self.invincible = False  # 無敵状態かどうか
        self.invincible_timer = 0  # 無敵時間のタイマー
        self.blink_timer = 0  # 点滅用タイマー
        
        # 弾の状態を管理するリスト
        self.bullets = []
        self.bullet_speed = 4
        self.bullet_size = 2
        
        # 経験値トークンの状態を管理するリスト
        self.exp_tokens = []
        self.exp_token_size = 4
        self.exp_token_speed = 1.5
        self.exp_count = 0  # 獲得経験値トークン数
        self.skills = []  # 獲得したスキル
        self.satellites = []  # 衛星のリスト
        self.show_skill_select = False  # スキル選択画面表示フラグ
        self.skill_options = []  # 表示するスキルオプション
        
        # 敵の状態を管理するリスト
        self.enemies = []
        self.enemy_size = 8
        self.enemy_speed = 1.5
        self.spawn_interval = 30
        self.spawn_timer = 0
        
        # クロスヘアの設定
        self.crosshair_size = 5
        self.crosshair_color = 8  # 赤色
        
        # 発射間隔の設定
        self.bullet_cooldown = 0
        self.cooldown_time = 20  # 初期発射間隔
        self.min_cooldown = 5    # 最小発射間隔
        
        # ゲームの状態を管理する変数
        self.game_over = False
        self.paused = False  # 一時停止状態
        self.score = 0  # スコアを初期化
        self.selected_skill = None  # 選択されたスキル
        self.last_key_pressed = None  # 最後に押されたキー
        
        # 日本語フォントを初期化
        self.font = pyxel.Font("assets/k8x12.bdf")
        
        # ゲームを開始
        pyxel.run(self.update, self.draw)
    
    def spawn_enemy(self):
        # ランダムな角度を生成（0-360度）
        angle = random.uniform(0, math.pi * 2)
        
        # スポーン位置（プレイヤーから離れた位置）
        spawn_radius = 180
        spawn_x = self.player_x + math.cos(angle) * spawn_radius
        spawn_y = self.player_y + math.sin(angle) * spawn_radius
        
        # 敵のタイプをランダムに設定
        enemy_type = random.choice(['red', 'blue', 'green'])
        
        # 敵をリストに追加
        self.enemies.append({
            'x': spawn_x,
            'y': spawn_y,
            'angle': angle,
            'type': enemy_type,
            'shoot_timer': 0  # 青い敵の弾発射用タイマー
        })
    
    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.game_over = False
                self.reset_game()
            return
            
        if self.show_skill_select:
            self.update_skill_select()
        else:
            self.update_game()
            
    def update_game(self):
        # ゲームのメイン更新処理
        # プレイヤーの移動（WASD）
        if pyxel.btn(pyxel.KEY_W):
            self.player_y -= self.player_speed
        if pyxel.btn(pyxel.KEY_S):
            self.player_y += self.player_speed
        if pyxel.btn(pyxel.KEY_A):
            self.player_x -= self.player_speed
        if pyxel.btn(pyxel.KEY_D):
            self.player_x += self.player_speed
        
        # 敵のスポーン処理
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0
        
        # 敵の更新
        for enemy in self.enemies[:]:
            # 敵のタイプに応じた行動
            if enemy['type'] == 'red':
                # 赤い敵：プレイヤーに突進
                dx = self.player_x - enemy['x']
                dy = self.player_y - enemy['y']
                angle = math.atan2(dy, dx)
                enemy['x'] += math.cos(angle) * self.enemy_speed * 1.5  # 赤い敵は速い
                enemy['y'] += math.sin(angle) * self.enemy_speed * 1.5
            elif enemy['type'] == 'blue':
                # 青い敵：ゆっくり移動しつつ弾を発射
                dx = self.player_x - enemy['x']
                dy = self.player_y - enemy['y']
                angle = math.atan2(dy, dx)
                enemy['x'] += math.cos(angle) * self.enemy_speed * 0.7  # 青い敵は遅い
                enemy['y'] += math.sin(angle) * self.enemy_speed * 0.7
                
                # 弾を発射
                enemy['shoot_timer'] += 1
                if enemy['shoot_timer'] >= 60:  # 1秒ごとに発射
                    self.bullets.append({
                        'x': enemy['x'],
                        'y': enemy['y'],
                        'vx': math.cos(angle) * self.bullet_speed,
                        'vy': math.sin(angle) * self.bullet_speed,
                        'from_enemy': True  # 敵の弾であることを示す
                    })
                    enemy['shoot_timer'] = 0
            else:
                # 緑の敵：プレイヤーに超低速で近づく
                dx = self.player_x - enemy['x']
                dy = self.player_y - enemy['y']
                angle = math.atan2(dy, dx)
                enemy['x'] += math.cos(angle) * self.enemy_speed * 0.2  # 通常速度の20%
                enemy['y'] += math.sin(angle) * self.enemy_speed * 0.2
                
                # プレイヤーとの距離を計算
                dx = self.player_x - enemy['x']
                dy = self.player_y - enemy['y']
            
            # プレイヤーと敵の衝突判定
            if (math.sqrt(dx * dx + dy * dy) < self.player_size and
                not self.invincible):
                self.player_hp -= 3  # 体当たりで3ダメージ
                if enemy in self.enemies:
                    self.enemies.remove(enemy)  # 敵を消す
                if self.player_hp <= 0:
                    self.game_over = True
                    break
                # 無敵状態を有効にする
                self.invincible = True
                self.invincible_timer = 180  # 3秒間無敵（60fps * 3）
            
            # プレイヤーと敵の弾の衝突判定
            for bullet in self.bullets[:]:
                if bullet.get('from_enemy', False):
                    dx = bullet['x'] - self.player_x
                    dy = bullet['y'] - self.player_y
                    if (math.sqrt(dx * dx + dy * dy) < self.player_size and
                        not self.invincible):
                        self.player_hp -= 1  # 敵の弾で1ダメージ
                        if self.player_hp <= 0:
                            self.player_hp = 0
                            self.game_over = True
                        # 弾を消滅させる
                        self.bullets.remove(bullet)
                        break
        
        # 無敵状態の更新
        if self.invincible:
            self.invincible_timer -= 1
            self.blink_timer += 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.blink_timer = 0
                
        # 衛星の更新
        for satellite in self.satellites:
            satellite.update()

        # 弾の発射間隔を更新
        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1

        # デバッグ用：Tキーで経験値トークンを20個獲得
        if pyxel.btnp(pyxel.KEY_T):
            self.exp_count += 20
            if self.exp_count >= 20:
                self.show_skill_select = True
                self.paused = True  # ゲームを一時停止
                self.generate_skill_options()
                
        # スキル選択が終了したら一時停止を解除
        if not self.show_skill_select:
            self.paused = False

        # スキル選択処理
        if self.show_skill_select:
            if pyxel.btnp(pyxel.KEY_1, hold=0, repeat=0):
                self.last_key_pressed = '1'
                self.selected_skill = self.skill_options[0]['name']
                self.skill_options[0]['effect']()
                self.show_skill_select = False
                return
            if pyxel.btnp(pyxel.KEY_2, hold=0, repeat=0):
                self.last_key_pressed = '2'
                self.selected_skill = self.skill_options[1]['name']
                self.skill_options[1]['effect']()
                self.show_skill_select = False
                return
            if pyxel.btnp(pyxel.KEY_3, hold=0, repeat=0):
                self.last_key_pressed = '3'
                self.selected_skill = self.skill_options[2]['name']
                self.skill_options[2]['effect']()
                self.show_skill_select = False
                return
        # マウスクリックで弾を発射
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.bullet_cooldown <= 0:
            # 弾の速度ベクトルを計算
            dx = pyxel.mouse_x - 128
            dy = pyxel.mouse_y - 128
            angle = math.atan2(dy, dx)
            bullet_vx = math.cos(angle) * self.bullet_speed
            bullet_vy = math.sin(angle) * self.bullet_speed
            
            # 弾を追加
            self.bullets.append({
                'x': self.player_x,
                'y': self.player_y,
                'vx': bullet_vx,
                'vy': bullet_vy
            })
            
            # 発射間隔をリセット
            self.bullet_cooldown = self.cooldown_time
        
        # 弾の更新
        for bullet in self.bullets[:]:
            # 弾を移動
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            
            # 画面外に出た弾を削除
            screen_x = bullet['x'] - self.player_x + 128
            screen_y = bullet['y'] - self.player_y + 128
            if (screen_x < 0 or screen_x > 256 or
                screen_y < 0 or screen_y > 256):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue
            
            # 弾と敵の衝突判定（敵自身の弾は無視）
            for enemy in self.enemies[:]:
                dx = bullet['x'] - enemy['x']
                dy = bullet['y'] - enemy['y']
                if (math.sqrt(dx * dx + dy * dy) < self.enemy_size and
                    not bullet.get('from_enemy', False)):
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                        self.score += 1  # スコアを増加
                        # 経験値トークンを生成
                        self.exp_tokens.append({
                            'x': enemy['x'],
                            'y': enemy['y']
                        })
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
        
        # 経験値トークンの更新
        for exp_token in self.exp_tokens[:]:
            # 画面外に出たトークンを削除
            screen_x = exp_token['x'] - self.player_x + 128
            screen_y = exp_token['y'] - self.player_y + 128
            if (screen_x < 0 or screen_x > 256 or
                screen_y < 0 or screen_y > 256):
                if exp_token in self.exp_tokens:
                    self.exp_tokens.remove(exp_token)
                continue
            
            # プレイヤーと経験値トークンの衝突判定
            dx = exp_token['x'] - self.player_x
            dy = exp_token['y'] - self.player_y
            if math.sqrt(dx * dx + dy * dy) < self.player_size:
                if exp_token in self.exp_tokens:
                    self.exp_tokens.remove(exp_token)
                    self.exp_count += 1  # 経験値を1増加
                    # 経験値が20の倍数ならスキル選択画面を表示
                    if self.exp_count % 20 == 0:
                        self.show_skill_select = True
                        self.paused = True  # ゲームを一時停止
                        self.generate_skill_options()
                # 発射間隔を短くする（最小値まで）
                if self.cooldown_time > self.min_cooldown:
                    self.cooldown_time -= 1

    def update_skill_select(self):
        # スキル選択の更新処理
        if pyxel.btnp(pyxel.KEY_1, hold=0, repeat=0):
            self.last_key_pressed = '1'
            self.selected_skill = self.skill_options[0]['name']
            self.skill_options[0]['effect']()
            self.show_skill_select = False
            return
        if pyxel.btnp(pyxel.KEY_2, hold=0, repeat=0):
            self.last_key_pressed = '2'
            self.selected_skill = self.skill_options[1]['name']
            self.skill_options[1]['effect']()
            self.show_skill_select = False
            return
        if pyxel.btnp(pyxel.KEY_3, hold=0, repeat=0):
            self.last_key_pressed = '3'
            self.selected_skill = self.skill_options[2]['name']
            self.skill_options[2]['effect']()
            self.show_skill_select = False
            return
            
    def update_game(self):
        # ゲームのメイン更新処理
        # プレイヤーの移動（WASD）
        if pyxel.btn(pyxel.KEY_W):
            self.player_y -= self.player_speed
        if pyxel.btn(pyxel.KEY_S):
            self.player_y += self.player_speed
        if pyxel.btn(pyxel.KEY_A):
            self.player_x -= self.player_speed
        if pyxel.btn(pyxel.KEY_D):
            self.player_x += self.player_speed
        
        # 敵のスポーン処理
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0
        
        # 敵の更新
        for enemy in self.enemies[:]:
            # 敵のタイプに応じた行動
            if enemy['type'] == 'red':
                # 赤い敵：プレイヤーに突進
                dx = self.player_x - enemy['x']
                dy = self.player_y - enemy['y']
                angle = math.atan2(dy, dx)
                enemy['x'] += math.cos(angle) * self.enemy_speed * 1.5  # 赤い敵は速い
                enemy['y'] += math.sin(angle) * self.enemy_speed * 1.5
            elif enemy['type'] == 'blue':
                # 青い敵：ゆっくり移動しつつ弾を発射
                dx = self.player_x - enemy['x']
                dy = self.player_y - enemy['y']
                angle = math.atan2(dy, dx)
                enemy['x'] += math.cos(angle) * self.enemy_speed * 0.7  # 青い敵は遅い
                enemy['y'] += math.sin(angle) * self.enemy_speed * 0.7
                
                # 弾を発射
                enemy['shoot_timer'] += 1
                if enemy['shoot_timer'] >= 60:  # 1秒ごとに発射
                    self.bullets.append({
                        'x': enemy['x'],
                        'y': enemy['y'],
                        'vx': math.cos(angle) * self.bullet_speed,
                        'vy': math.sin(angle) * self.bullet_speed,
                        'from_enemy': True  # 敵の弾であることを示す
                    })
                    enemy['shoot_timer'] = 0
            else:
                # 緑の敵：プレイヤーに超低速で近づく
                dx = self.player_x - enemy['x']
                dy = self.player_y - enemy['y']
                angle = math.atan2(dy, dx)
                enemy['x'] += math.cos(angle) * self.enemy_speed * 0.2  # 通常速度の20%
                enemy['y'] += math.sin(angle) * self.enemy_speed * 0.2
                
                # プレイヤーとの距離を計算
                dx = self.player_x - enemy['x']
                dy = self.player_y - enemy['y']
            
            # プレイヤーと敵の衝突判定
            if (math.sqrt(dx * dx + dy * dy) < self.player_size and 
                not self.invincible):
                self.player_hp -= 3  # 体当たりで3ダメージ
                if enemy in self.enemies:
                    self.enemies.remove(enemy)  # 敵を消す
                if self.player_hp <= 0:
                    self.game_over = True
                    break
                # 無敵状態を有効にする
                self.invincible = True
                self.invincible_timer = 180  # 3秒間無敵（60fps * 3）
            
            # プレイヤーと敵の弾の衝突判定
            for bullet in self.bullets[:]:
                if bullet.get('from_enemy', False):
                    dx = bullet['x'] - self.player_x
                    dy = bullet['y'] - self.player_y
                    if (math.sqrt(dx * dx + dy * dy) < self.player_size and
                        not self.invincible):
                        self.player_hp -= 1  # 敵の弾で1ダメージ
                        if self.player_hp <= 0:
                            self.player_hp = 0
                            self.game_over = True
                        # 弾を消滅させる
                        self.bullets.remove(bullet)
                        break
        
        # 無敵状態の更新
        if self.invincible:
            self.invincible_timer -= 1
            self.blink_timer += 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.blink_timer = 0
                
        # 衛星の更新
        for satellite in self.satellites:
            satellite.update()

        # 弾の発射間隔を更新
        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1

        # デバッグ用：Tキーで経験値トークンを20個獲得
        if pyxel.btnp(pyxel.KEY_T):
            self.exp_count += 20
            if self.exp_count >= 20:
                self.show_skill_select = True
                self.paused = True  # ゲームを一時停止
                self.generate_skill_options()
                
        # スキル選択が終了したら一時停止を解除
        if not self.show_skill_select:
            self.paused = False

        # マウスクリックで弾を発射
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.bullet_cooldown <= 0:
            # 弾の速度ベクトルを計算
            dx = pyxel.mouse_x - 128
            dy = pyxel.mouse_y - 128
            angle = math.atan2(dy, dx)
            bullet_vx = math.cos(angle) * self.bullet_speed
            bullet_vy = math.sin(angle) * self.bullet_speed
            
            # 弾を追加
            self.bullets.append({
                'x': self.player_x,
                'y': self.player_y,
                'vx': bullet_vx,
                'vy': bullet_vy
            })
            
            # 発射間隔をリセット
            self.bullet_cooldown = self.cooldown_time
        
        # 弾の更新
        for bullet in self.bullets[:]:
            # 弾を移動
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            
            # 画面外に出た弾を削除
            screen_x = bullet['x'] - self.player_x + 128
            screen_y = bullet['y'] - self.player_y + 128
            if (screen_x < 0 or screen_x > 256 or
                screen_y < 0 or screen_y > 256):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue
            
            # 弾と敵の衝突判定（敵自身の弾は無視）
            for enemy in self.enemies[:]:
                dx = bullet['x'] - enemy['x']
                dy = bullet['y'] - enemy['y']
                if (math.sqrt(dx * dx + dy * dy) < self.enemy_size and
                    not bullet.get('from_enemy', False)):
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                        self.score += 1  # スコアを増加
                        # 経験値トークンを生成
                        self.exp_tokens.append({
                            'x': enemy['x'],
                            'y': enemy['y']
                        })
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
        
        # 経験値トークンの更新
        for exp_token in self.exp_tokens[:]:
            # 画面外に出たトークンを削除
            screen_x = exp_token['x'] - self.player_x + 128
            screen_y = exp_token['y'] - self.player_y + 128
            if (screen_x < 0 or screen_x > 256 or
                screen_y < 0 or screen_y > 256):
                if exp_token in self.exp_tokens:
                    self.exp_tokens.remove(exp_token)
                continue
            
            # プレイヤーと経験値トークンの衝突判定
            dx = exp_token['x'] - self.player_x
            dy = exp_token['y'] - self.player_y
            if math.sqrt(dx * dx + dy * dy) < self.player_size:
                if exp_token in self.exp_tokens:
                    self.exp_tokens.remove(exp_token)
                    self.exp_count += 1  # 経験値を1増加
                    # 経験値が20の倍数ならスキル選択画面を表示
                    if self.exp_count % 20 == 0:
                        self.show_skill_select = True
                        self.paused = True  # ゲームを一時停止
                        self.generate_skill_options()
                # 発射間隔を短くする（最小値まで）
                if self.cooldown_time > self.min_cooldown:
                    self.cooldown_time -= 1
    
    class Satellite:
        def __init__(self, player):
            self.player = player
            self.angle = 0
            self.distance = 40  # プレイヤーからの距離（増加）
            self.speed = 0.05  # 回転速度（増加）
            self.size = 2
            self.color = 9  # オレンジ色
            self.damage = 1  # 与えるダメージ

        def update(self):
            # 衛星の位置を更新
            self.angle += self.speed
            if self.angle > math.pi * 2:
                self.angle -= math.pi * 2
            
            # 敵との衝突判定
            for enemy in self.player.enemies[:]:
                dx = self.get_x() - enemy['x']
                dy = self.get_y() - enemy['y']
                if math.sqrt(dx * dx + dy * dy) < self.size + self.player.enemy_size:
                    # 敵にダメージを与える
                    self.player.enemies.remove(enemy)
                    self.player.score += 1

        def get_x(self):
            return self.player.player_x + math.cos(self.angle) * self.distance

        def get_y(self):
            return self.player.player_y + math.sin(self.angle) * self.distance

        def draw(self):
            # 衛星を描画
            screen_x = self.get_x() - self.player.player_x + 128
            screen_y = self.get_y() - self.player.player_y + 128
            pyxel.circ(screen_x, screen_y, self.size, self.color)

    def generate_skill_options(self):
        # スキルオプションを生成
        self.skill_options = [
            {
                'name': '衛星砲',
                'description': 'プレイヤーを周回する補助砲台を追加',
                'effect': lambda: self.satellites.append(self.Satellite(self))
            },
            {
                'name': '移動速度アップ',
                'description': 'プレイヤーの移動速度が上がる',
                'effect': lambda: setattr(self, 'player_speed', self.player_speed + 1)
            },
            {
                'name': '最大HPアップ',
                'description': 'プレイヤーの最大HPが増える',
                'effect': lambda: setattr(self, 'max_hp', self.max_hp + 2)
            }
        ]

    def draw(self):
        # 画面を消去
        pyxel.cls(0)

        # 背景を描画（定期的なドット）
        for x in range(-256, 256, 16):  # プレイヤーの移動範囲を考慮
            for y in range(-256, 256, 16):
                # プレイヤーの移動に合わせて背景をスクロール（移動方向と逆向きにスクロール）
                screen_x = (x - self.player_x) % 256
                screen_y = (y - self.player_y) % 256
                pyxel.pset(screen_x, screen_y, 3)  # ドットの色を設定（色番号3）

        if self.game_over:
            # ゲームオーバー画面の描画
            pyxel.text(100, 116, "GAME OVER", 7)
            pyxel.text(76, 132, "Press 'R' to restart", 7)
        else:
            # プレイヤーを描画（画面中央に固定）
            screen_x = 128  # プレイヤーのX座標（画面中央）
            screen_y = 128  # プレイヤーのY座標（画面中央）
            # 無敵状態で点滅表示
            if not self.invincible or (self.blink_timer // 10) % 2 == 0:
                pyxel.circ(screen_x, screen_y, self.player_size // 2, 7)
            
            # HPゲージを描画
            gauge_width = 20
            gauge_height = 3
            gauge_x = screen_x - gauge_width // 2
            gauge_y = screen_y + self.player_size // 2 + 5
            # 背景
            pyxel.rect(gauge_x, gauge_y, gauge_width, gauge_height, 1)
            # HPバー
            hp_width = int(gauge_width * (self.player_hp / self.max_hp))
            pyxel.rect(gauge_x, gauge_y, hp_width, gauge_height, 8)
            
            # 敵を描画
            for enemy in self.enemies:
                screen_x = enemy['x'] - self.player_x + 128
                screen_y = enemy['y'] - self.player_y + 128
                # 敵のタイプに応じた色で描画
                if enemy['type'] == 'red':
                    color = 8  # 赤
                elif enemy['type'] == 'blue':
                    color = 12  # 青
                else:
                    color = 11  # 緑
                pyxel.rect(screen_x - self.enemy_size//2, screen_y - self.enemy_size//2, 
                          self.enemy_size, self.enemy_size, color)
            
            # 弾を描画
            for bullet in self.bullets:
                screen_x = bullet['x'] - self.player_x + 128
                screen_y = bullet['y'] - self.player_y + 128
                # 弾の種類に応じて色を変更
                color = 12 if bullet.get('from_enemy', False) else 8
                pyxel.rect(screen_x - self.bullet_size//2, screen_y - self.bullet_size//2, 
                           self.bullet_size, self.bullet_size, color)
            
            # 経験値トークンを描画
            for exp_token in self.exp_tokens:
                screen_x = exp_token['x'] - self.player_x + 128
                screen_y = exp_token['y'] - self.player_y + 128
                pyxel.circ(screen_x, screen_y, self.exp_token_size, 10)  # 黄色で描画
            
            # クロスヘアを描画
            size = self.crosshair_size
            x = pyxel.mouse_x
            y = pyxel.mouse_y
            pyxel.line(x - size, y, x + size, y, self.crosshair_color)
            pyxel.line(x, y - size, x, y + size, self.crosshair_color)
            
            # 再発射ゲージを描画
            if self.bullet_cooldown > 0:
                gauge_width = 20
                gauge_height = 3
                gauge_x = x - gauge_width // 2
                gauge_y = y + size + 5
                # 背景
                pyxel.rect(gauge_x, gauge_y, gauge_width, gauge_height, 1)
                # 現在のクールダウンの進捗
                progress = 1 - (self.bullet_cooldown / self.cooldown_time)
                filled_width = int(gauge_width * progress)
                pyxel.rect(gauge_x, gauge_y, filled_width, gauge_height, 8)
            
            # 衛星を描画
            for satellite in self.satellites:
                satellite.draw()

            # プレイヤー情報を表示
            pyxel.text(5, 5, f"X: {self.player_x:.1f} Y: {self.player_y:.1f}", 7)
            pyxel.text(5, 235, f"Score: {self.score} Exp: {self.exp_count}", 7)

            # スキル選択画面を表示
            if self.show_skill_select:
                # 背景
                pyxel.rect(50, 50, 156, 156, 1)
                # タイトル
                draw_text_with_border(80, 50, "スキルを選択", 7, 5, self.font)
                # 操作説明
                draw_text_with_border(60, 65, "キーボード上部の1,2,3キーで選択", 7, 5, self.font)
                # スキルオプションを表示
                for i, option in enumerate(self.skill_options):
                    y = 90 + i * 35
                    draw_text_with_border(60, y, f"{i+1}. {option['name']}", 7, 5, self.font)
                    draw_text_with_border(60, y + 15, option['description'], 5, 1, self.font)
                
App()
