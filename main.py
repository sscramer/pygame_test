import pyxel
import math
import random

def draw_text_with_border(x, y, s, col, bcol, font):
    """
    縁取り文字を描画するヘルパー関数
    """
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
        """
        ゲームの初期化処理を行うコンストラクタ
        """
        # ゲームウィンドウを初期化（幅256px、高さ256px）
        pyxel.init(256, 256, title="My Pyxel Game", capture_scale=1, capture_sec=0)
        
        # プレイヤーの初期状態を設定
        self.player_x = 0  # プレイヤーのX座標
        self.player_y = 0  # プレイヤーのY座標
        self.player_size = 8  # プレイヤーのサイズ（半径）
        self.player_speed = 2  # プレイヤーの移動速度
        self.max_hp = 10  # プレイヤーの最大HP
        self.player_hp = self.max_hp  # プレイヤーの現在HP
        self.invincible = False  # 無敵状態かどうか
        self.invincible_timer = 0  # 無敵状態の残り時間
        self.blink_timer = 0  # 点滅用タイマー
        
        # 弾関連の設定
        self.bullets = []  # 弾のリスト
        self.bullet_speed = 4  # 弾の速度
        self.bullet_size = 2  # 弾のサイズ
        
        # 経験値トークン関連の設定
        self.exp_tokens = []  # 経験値トークンのリスト
        self.exp_token_size = 4  # トークンのサイズ
        self.exp_token_speed = 1.5  # トークンの移動速度
        self.exp_count = 0  # 獲得した経験値
        
        # スキル関連の設定
        self.skills = []  # 獲得したスキルのリスト
        self.satellites = []  # 衛星オブジェクトのリスト
        self.show_skill_select = False  # スキル選択画面を表示するか
        self.skill_options = []  # 選択可能なスキルのリスト
        self.selected_skill = None  # 選択されたスキル
        
        # 敵関連の設定
        self.enemies = []  # 敵のリスト
        self.enemy_size = 8  # 敵のサイズ
        self.enemy_speed = 1.5  # 敵の移動速度
        self.spawn_interval = 30  # 敵のスポーン間隔
        self.spawn_timer = 0  # 敵スポーン用タイマー
        
        # クロスヘアの設定
        self.crosshair_size = 5  # クロスヘアのサイズ
        self.crosshair_color = 8  # クロスヘアの色（赤色）
        
        # 弾の発射間隔設定
        self.bullet_cooldown = 0  # 弾の発射クールダウン
        self.cooldown_time = 20  # 初期クールダウン時間
        self.min_cooldown = 5    # 最小クールダウン時間
        
        # ゲーム状態の管理
        self.game_over = False  # ゲームオーバー状態か
        self.paused = False  # ゲームが一時停止中か
        self.score = 0  # 現在のスコア
        self.level = 1  # 現在のレベル
        self.base_spawn_interval = 30  # 敵スポーンの基本間隔
        self.last_key_pressed = None  # 最後に押されたキー
        
        # 日本語フォントを初期化
        self.font = pyxel.Font("assets/k8x12.bdf")
        
        # ゲーム開始
        pyxel.run(self.update, self.draw)
    
    def update(self):
        """
        メインの更新メソッド。Pyxel はここを1フレームごとに呼び出す。
        """
        # ゲームオーバー時
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.game_over = False
                self.reset_game()
            return
        
        # スキル選択画面が表示されている場合
        if self.show_skill_select:
            self.update_skill_select()
        else:
            self.update_game()

    def update_skill_select(self):
        """
        スキル選択画面の更新処理
        """
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
        """
        メインのゲームロジックをすべてここで処理
        1フレームごとに呼び出され、以下の処理を行う：
        - プレイヤーの移動と攻撃
        - 敵のスポーンと移動
        - 弾と敵の衝突判定
        - 経験値トークンの処理
        - ゲーム状態の更新
        """
        # ------------------------------------------------------------
        # デバッグ用：Tキーで経験値トークンを20個獲得
        # ------------------------------------------------------------
        if pyxel.btnp(pyxel.KEY_T, hold=0, repeat=0):
            print("T key pressed")  # デバッグ用出力
            self.exp_count += 20
            self.score += 20
            print(f"Debug: Score increased to {self.score}, Exp increased to {self.exp_count}")
            if self.exp_count >= 20:
                self.show_skill_select = True
                self.paused = True
                self.generate_skill_options()

        # ------------------------------------------------------------
        # レベルアップ判定：スコアに応じてレベルを更新し、敵の発生間隔を短縮
        # ------------------------------------------------------------
        new_level = self.score // 20 + 1
        if new_level > self.level:
            self.level = new_level
            self.spawn_interval = max(10, self.base_spawn_interval - self.level * 2)

        # ------------------------------------------------------------
        # プレイヤー移動（WASD）
        # ------------------------------------------------------------
        if pyxel.btn(pyxel.KEY_W):
            self.player_y -= self.player_speed
        if pyxel.btn(pyxel.KEY_S):
            self.player_y += self.player_speed
        if pyxel.btn(pyxel.KEY_A):
            self.player_x -= self.player_speed
        if pyxel.btn(pyxel.KEY_D):
            self.player_x += self.player_speed

        # ------------------------------------------------------------
        # 敵のスポーン
        # ------------------------------------------------------------
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0

        # ------------------------------------------------------------
        # 敵の挙動と衝突判定
        # ------------------------------------------------------------
        for enemy in self.enemies[:]:
            dx = self.player_x - enemy['x']
            dy = self.player_y - enemy['y']
            angle = math.atan2(dy, dx)
            
            if enemy['type'] == 'red':
                # 赤い敵：プレイヤーに高速突進
                enemy['x'] += math.cos(angle) * self.enemy_speed * 1.5
                enemy['y'] += math.sin(angle) * self.enemy_speed * 1.5
            elif enemy['type'] == 'blue':
                # 青い敵：ゆっくり移動 + 定期的に弾発射
                enemy['x'] += math.cos(angle) * self.enemy_speed * 0.7
                enemy['y'] += math.sin(angle) * self.enemy_speed * 0.7
                enemy['shoot_timer'] += 1
                if enemy['shoot_timer'] >= 60:  # 1秒ごとに発射
                    self.bullets.append({
                        'x': enemy['x'],
                        'y': enemy['y'],
                        'vx': math.cos(angle) * self.bullet_speed,
                        'vy': math.sin(angle) * self.bullet_speed,
                        'from_enemy': True
                    })
                    enemy['shoot_timer'] = 0
            else:
                # 緑の敵：超低速で近づく
                enemy['x'] += math.cos(angle) * self.enemy_speed * 0.2
                enemy['y'] += math.sin(angle) * self.enemy_speed * 0.2
            
            # プレイヤーと敵の衝突判定
            dist_pe = math.hypot(self.player_x - enemy['x'], self.player_y - enemy['y'])
            if dist_pe < self.player_size and not self.invincible:
                self.player_hp -= 3
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                if self.player_hp <= 0:
                    self.game_over = True
                    break
                # プレイヤーを無敵状態に
                self.invincible = True
                self.invincible_timer = 180  # 3秒

        # ------------------------------------------------------------
        # 敵の弾とプレイヤーの衝突判定
        # ------------------------------------------------------------
        for bullet in self.bullets[:]:
            if bullet.get('from_enemy', False):
                dist_pb = math.hypot(bullet['x'] - self.player_x, bullet['y'] - self.player_y)
                if dist_pb < self.player_size and not self.invincible:
                    self.player_hp -= 1
                    if self.player_hp <= 0:
                        self.player_hp = 0
                        self.game_over = True
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

        # ------------------------------------------------------------
        # 無敵状態の時間管理（点滅処理）
        # ------------------------------------------------------------
        if self.invincible:
            self.invincible_timer -= 1
            self.blink_timer += 1
            if self.invincible_timer <= 0:
                self.invincible = False
                self.blink_timer = 0

        # ------------------------------------------------------------
        # 衛星（スキル獲得オブジェクト）の更新
        # ------------------------------------------------------------
        for satellite in self.satellites:
            satellite.update()
        
        # ------------------------------------------------------------
        # 弾の発射クールダウン更新
        # ------------------------------------------------------------
        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1

        # ------------------------------------------------------------
        # マウスクリックで弾を発射
        # ------------------------------------------------------------
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.bullet_cooldown <= 0:
            dx = pyxel.mouse_x - 128
            dy = pyxel.mouse_y - 128
            angle = math.atan2(dy, dx)
            bullet_vx = math.cos(angle) * self.bullet_speed
            bullet_vy = math.sin(angle) * self.bullet_speed
            
            self.bullets.append({
                'x': self.player_x,
                'y': self.player_y,
                'vx': bullet_vx,
                'vy': bullet_vy,
                'from_enemy': False
            })
            
            self.bullet_cooldown = self.cooldown_time

        # ------------------------------------------------------------
        # 弾の更新 & 敵との衝突判定
        # ------------------------------------------------------------
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
            
            # プレイヤーが撃った弾と敵の衝突判定
            if not bullet.get('from_enemy', False):
                for enemy in self.enemies[:]:
                    dist_be = math.hypot(bullet['x'] - enemy['x'], bullet['y'] - enemy['y'])
                    if dist_be < self.enemy_size:
                        # 敵を倒す
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                            self.score += 1
                            # 経験値トークンを生成
                            self.exp_tokens.append({
                                'x': enemy['x'],
                                'y': enemy['y']
                            })
                        # 弾を消す
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break

        # ------------------------------------------------------------
        # 経験値トークンの更新
        # ------------------------------------------------------------
        for exp_token in self.exp_tokens[:]:
            dx = exp_token['x'] - self.player_x
            dy = exp_token['y'] - self.player_y
            distance = math.hypot(dx, dy)
            
            # 30ピクセル以内なら吸い寄せ
            if distance < 30:
                angle = math.atan2(dy, dx)
                exp_token['x'] -= math.cos(angle) * self.exp_token_speed * 2
                exp_token['y'] -= math.sin(angle) * self.exp_token_speed * 2

            # プレイヤーとトークンの衝突判定
            if distance < self.player_size:
                if exp_token in self.exp_tokens:
                    self.exp_tokens.remove(exp_token)
                    self.exp_count += 1
                    # exp_countが20の倍数ならスキル選択
                    if self.exp_count % 20 == 0:
                        self.show_skill_select = True
                        self.paused = True
                        self.generate_skill_options()

    def spawn_enemy(self):
        """
        一定距離離れた円周上に敵をスポーンさせる
        """
        angle = random.uniform(0, math.pi * 2)
        spawn_radius = 180
        spawn_x = self.player_x + math.cos(angle) * spawn_radius
        spawn_y = self.player_y + math.sin(angle) * spawn_radius
        
        enemy_type = random.choice(['red', 'blue', 'green'])
        
        self.enemies.append({
            'x': spawn_x,
            'y': spawn_y,
            'angle': angle,
            'type': enemy_type,
            'shoot_timer': 0
        })

    class Satellite:
        """
        衛星オブジェクト：プレイヤーの周囲を回転し、敵に衝突して倒す。
        スキルとして獲得可能なオブジェクトで、以下の機能を持つ：
        - プレイヤーの周囲を一定速度で回転
        - 敵との衝突判定
        - 敵を倒すとスコアを加算
        """
        def __init__(self, player):
            """
            衛星オブジェクトの初期化
            Args:
                player (App): プレイヤーオブジェクトへの参照
            """
            self.player = player  # プレイヤーオブジェクト
            self.angle = 0  # 現在の回転角度
            self.distance = 40  # プレイヤーからの距離
            self.speed = 0.05   # 回転速度（ラジアン/フレーム）
            self.size = 2  # 衛星のサイズ（半径）
            self.color = 9      # 衛星の色（オレンジ色）
            self.damage = 1     # 与えるダメージ（現在は即死扱い）

        def update(self):
            """
            衛星の状態を更新するメソッド
            1フレームごとに呼び出され、以下の処理を行う：
            - 回転角度を更新
            - 敵との衝突判定
            """
            # 回転角を進める
            self.angle += self.speed
            if self.angle > math.pi * 2:
                self.angle -= math.pi * 2
            
            # 敵との衝突判定
            for enemy in self.player.enemies[:]:
                dist_se = math.hypot(self.get_x() - enemy['x'], self.get_y() - enemy['y'])
                if dist_se < self.size + self.player.enemy_size:
                    # 衛星に当たった敵を倒す
                    self.player.enemies.remove(enemy)
                    self.player.score += 1
                    # 経験値トークンも落としたければここで追加してもよい

        def get_x(self):
            """
            衛星の現在のX座標を取得
            Returns:
                float: 衛星のX座標
            """
            return self.player.player_x + math.cos(self.angle) * self.distance

        def get_y(self):
            """
            衛星の現在のY座標を取得
            Returns:
                float: 衛星のY座標
            """
            return self.player.player_y + math.sin(self.angle) * self.distance

        def draw(self):
            """
            衛星を描画するメソッド
            プレイヤーを中心とした相対座標で描画する
            """
            screen_x = self.get_x() - self.player.player_x + 128
            screen_y = self.get_y() - self.player.player_y + 128
            pyxel.circ(screen_x, screen_y, self.size, self.color)

    def reset_game(self):
        """
        ゲームの状態を初期化する
        """
        self.player_x = 0
        self.player_y = 0
        self.player_hp = self.max_hp
        self.score = 0
        self.exp_count = 0
        self.bullets.clear()
        self.enemies.clear()
        self.exp_tokens.clear()
        self.skills.clear()
        self.satellites.clear()
        self.game_over = False
        self.paused = False
        self.show_skill_select = False
        self.cooldown_time = 20
        self.level = 1
        self.spawn_interval = self.base_spawn_interval

    def generate_skill_options(self):
        """
        スキル選択画面に表示するスキル一覧を生成
        """
        self.skill_options = [
            {
                'name': '衛星砲',
                'description': 'プレイヤーを周回する補助砲台を追加',
                'effect': lambda: self.satellites.append(self.Satellite(self))
            },
            {
                'name': '攻撃速度アップ',
                'description': '弾の発射間隔がより短くなる',
                'effect': lambda: setattr(self, 'cooldown_time', max(self.min_cooldown, self.cooldown_time - 2))
            },
            {
                'name': 'HP全回復',
                'description': 'プレイヤーのHPを最大値まで回復',
                'effect': lambda: setattr(self, 'player_hp', self.max_hp)
            }
        ]

    def draw(self):
        """
        メインの描画メソッド。Pyxel はここを1フレームごとに呼び出す。
        以下の要素を描画する：
        - 背景
        - プレイヤー
        - 敵
        - 弾
        - 経験値トークン
        - UI（スコア、HPゲージなど）
        - スキル選択画面（表示されている場合）
        """
        pyxel.cls(0)

        # 背景ドットを描画（マップスクロールのような演出）
        for x in range(-256, 256, 16):
            for y in range(-256, 256, 16):
                screen_x = (x - self.player_x) % 256
                screen_y = (y - self.player_y) % 256
                pyxel.pset(screen_x, screen_y, 3)

        # ------------------------------------------------------------
        # ゲームオーバー画面
        # ------------------------------------------------------------
        if self.game_over:
            pyxel.text(100, 116, "GAME OVER", 7)
            pyxel.text(76, 132, "Press 'R' to restart", 7)
            return

        # ------------------------------------------------------------
        # プレイヤー描画（画面中央に固定）
        # ------------------------------------------------------------
        screen_x = 128
        screen_y = 128
        # 無敵状態中はblink_timerに応じて点滅
        if not self.invincible or (self.blink_timer // 10) % 2 == 0:
            pyxel.circ(screen_x, screen_y, self.player_size // 2, 7)

        # HPゲージ（小さなバーをプレイヤー下に表示）
        gauge_width = 20
        gauge_height = 3
        gauge_x = screen_x - gauge_width // 2
        gauge_y = screen_y + self.player_size // 2 + 5
        pyxel.rect(gauge_x, gauge_y, gauge_width, gauge_height, 1)
        hp_width = int(gauge_width * (self.player_hp / self.max_hp))
        pyxel.rect(gauge_x, gauge_y, hp_width, gauge_height, 8)

        # ------------------------------------------------------------
        # 敵を描画
        # ------------------------------------------------------------
        for enemy in self.enemies:
            ex = enemy['x'] - self.player_x + 128
            ey = enemy['y'] - self.player_y + 128
            if enemy['type'] == 'red':
                color = 8   # 赤
            elif enemy['type'] == 'blue':
                color = 12  # 青
            else:
                color = 11  # 緑
            pyxel.rect(ex - self.enemy_size//2, ey - self.enemy_size//2, 
                       self.enemy_size, self.enemy_size, color)

        # ------------------------------------------------------------
        # 弾を描画
        # ------------------------------------------------------------
        for bullet in self.bullets:
            bx = bullet['x'] - self.player_x + 128
            by = bullet['y'] - self.player_y + 128
            color = 12 if bullet.get('from_enemy', False) else 8
            pyxel.rect(bx - self.bullet_size//2, by - self.bullet_size//2,
                       self.bullet_size, self.bullet_size, color)

        # ------------------------------------------------------------
        # 経験値トークンを描画
        # ------------------------------------------------------------
        for exp_token in self.exp_tokens:
            tx = exp_token['x'] - self.player_x + 128
            ty = exp_token['y'] - self.player_y + 128
            pyxel.circ(tx, ty, self.exp_token_size, 10)  # 黄色

        # ------------------------------------------------------------
        # クロスヘアを描画
        # ------------------------------------------------------------
        size = self.crosshair_size
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        pyxel.line(mx - size, my, mx + size, my, self.crosshair_color)
        pyxel.line(mx, my - size, mx, my + size, self.crosshair_color)

        # 再発射ゲージを描画
        if self.bullet_cooldown > 0:
            gauge_width = 20
            gauge_height = 3
            gauge_x = mx - gauge_width // 2
            gauge_y = my + size + 5
            pyxel.rect(gauge_x, gauge_y, gauge_width, gauge_height, 1)
            progress = 1 - (self.bullet_cooldown / self.cooldown_time)
            filled_width = int(gauge_width * progress)
            pyxel.rect(gauge_x, gauge_y, filled_width, gauge_height, 8)

        # ------------------------------------------------------------
        # 衛星を描画
        # ------------------------------------------------------------
        for satellite in self.satellites:
            satellite.draw()

        # ------------------------------------------------------------
        # UI系の描画（座標、スコア、経験値など）
        # ------------------------------------------------------------
        pyxel.text(5, 5, f"X: {self.player_x:.1f} Y: {self.player_y:.1f}", 7)
        pyxel.text(5, 235, f"Score: {self.score} Exp: {self.exp_count}", 7)

        # ------------------------------------------------------------
        # スキル選択画面の描画
        # ------------------------------------------------------------
        if self.show_skill_select:
            pyxel.rect(50, 50, 156, 156, 1)
            draw_text_with_border(80, 50, "スキルを選択", 7, 5, self.font)
            draw_text_with_border(60, 65, "キーボード上部の1,2,3キーで選択", 7, 5, self.font)
            for i, option in enumerate(self.skill_options):
                y = 90 + i * 35
                draw_text_with_border(60, y, f"{i+1}. {option['name']}", 7, 5, self.font)
                draw_text_with_border(60, y + 15, option['description'], 5, 1, self.font)

# アプリケーションを起動
App()
