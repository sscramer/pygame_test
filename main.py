import pyxel
import math
import random

def draw_text_with_border(x, y, s, col, bcol, font):
    """
    文字を描画する際に、縁取り（border）をつけるためのヘルパー関数。
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
        
        # -----------------------
        # プレイヤー関連の設定
        # -----------------------
        self.player_x = 0  # プレイヤーのX座標
        self.player_y = 0  # プレイヤーのY座標
        self.player_size = 8  # プレイヤーのサイズ（半径）
        self.player_speed = 2  # プレイヤーの移動速度
        self.max_hp = 10  # プレイヤーの最大HP
        self.player_hp = self.max_hp  # プレイヤーの現在HP
        self.invincible = False  # 無敵状態かどうか
        self.invincible_timer = 0  # 無敵状態の残り時間
        self.blink_timer = 0  # 点滅用タイマー
        
        # -----------------------
        # 弾関連の設定
        # -----------------------
        self.bullets = []  # 弾のリスト
        self.player_bullet_speed = 4  # プレイヤー弾の速度
        self.enemy_bullet_speed = 2   # 敵弾の速度
        self.bullet_size = 3  # 弾のサイズ
        
        # -----------------------
        # 経験値トークン関連の設定
        # -----------------------
        self.exp_tokens = []         # 経験値トークンのリスト
        self.exp_token_size = 4      # トークンのサイズ
        self.exp_token_speed = 1.5   # トークンの移動速度
        self.exp_count = 0           # 獲得した累計経験値
        
        # 「次のスキル取得に必要な累計経験値」を管理する仕組み
        self.skill_level = 1
        # スキル取得に必要な経験値: 5n^2 + 15n
        self.next_skill_threshold = self.get_skill_threshold(self.skill_level)
        
        # -----------------------
        # スキル関連の設定
        # -----------------------
        self.skills = []               # 獲得したスキルのリスト
        self.satellites = []           # 衛星オブジェクトのリスト
        self.show_skill_select = False # スキル選択画面を表示するか
        self.skill_options = []        # 選択可能なスキルのリスト
        self.selected_skill = None     # 選択されたスキル
        
        # -----------------------
        # 敵関連の設定
        # -----------------------
        self.enemies = []             # 敵のリスト
        self.enemy_size = 8           # 敵のサイズ
        self.enemy_speed = 1.5        # 敵の移動速度
        
        # 「通常の敵スポーン」まわり
        self.spawn_interval = 30      # 敵のスポーン間隔
        self.spawn_timer = 0          # 敵スポーン用タイマー
        
        # -----------------------
        # クロスヘア（照準）設定
        # -----------------------
        self.crosshair_size = 5       # クロスヘアのサイズ
        self.crosshair_color = 8      # クロスヘアの色（赤色）
        
        # -----------------------
        # 弾のクールダウン設定
        # -----------------------
        self.bullet_cooldown = 0      # 弾の発射クールダウン(フレーム)
        self.cooldown_time = 20       # 初期クールダウン時間
        self.min_cooldown = 5         # 最小クールダウン時間
        
        # -----------------------
        # ゲーム状態の管理
        # -----------------------
        self.game_over = False        # ゲームオーバー状態か
        self.paused = False           # ゲームが一時停止中か
        self.score = 0                # 現在のスコア
        self.level = 1                # 現在のレベル
        self.base_spawn_interval = 30 # 敵スポーンの基本間隔
        self.last_key_pressed = None  # 最後に押されたキー
        
        # -----------------------
        # イベント管理用タイマー
        # -----------------------
        self.event_timer = 0          # 特殊イベント用のタイマー
        
        # 日本語フォントを初期化
        self.font = pyxel.Font("assets/k8x12.bdf")
        
        # ゲーム開始
        pyxel.run(self.update, self.draw)

    def get_skill_threshold(self, nth):
        """
        n回目のスキル取得に必要な累計経験値を返す。
        5n^2 + 15n の形で増えていく。
        """
        return 5 * (nth**2) + 15 * nth
    
    def update(self):
        """
        メインの更新メソッド。Pyxel はここを1フレームごとに呼び出す。
        """
        # ゲームオーバー時の処理
        if self.game_over:
            # Rキーでリスタート
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
        # 1～3キーの入力でスキル決定
        if pyxel.btnp(pyxel.KEY_1, hold=0, repeat=0):
            self.last_key_pressed = '1'
            self.selected_skill = self.skill_options[0]['name']
            self.skill_options[0]['effect']()
            self.finish_skill_select()
            return
        if pyxel.btnp(pyxel.KEY_2, hold=0, repeat=0):
            self.last_key_pressed = '2'
            self.selected_skill = self.skill_options[1]['name']
            self.skill_options[1]['effect']()
            self.finish_skill_select()
            return
        if pyxel.btnp(pyxel.KEY_3, hold=0, repeat=0):
            self.last_key_pressed = '3'
            self.selected_skill = self.skill_options[2]['name']
            self.skill_options[2]['effect']()
            self.finish_skill_select()
            return

    def finish_skill_select(self):
        """
        スキル選択が終わった後の処理。
        - スキルウィンドウを閉じる
        - 次のスキル閾値を再計算する
        """
        self.show_skill_select = False
        self.paused = False
        
        # 次のスキル閾値を設定（n回目のスキル取得 → n+1回目の閾値へ）
        self.skill_level += 1
        self.next_skill_threshold = self.get_skill_threshold(self.skill_level)

    def update_game(self):
        """
        メインのゲームロジックをすべてここで処理
        1フレームごとに呼び出され、以下の処理を行う：
        - プレイヤーの移動と攻撃
        - 敵のスポーンと移動
        - 特殊イベントの処理（一定時間ごとの包囲や大群）
        - 弾と敵の衝突判定
        - 経験値トークンの処理
        - ゲーム状態の更新
        """
        # ------------------------------------------------------------
        # デバッグ用：Tキーで経験値トークンを20個獲得
        # ------------------------------------------------------------
        if pyxel.btnp(pyxel.KEY_T, hold=0, repeat=0):
            self.exp_count += 20
            self.score += 20  # スコアも上げておく

        # ------------------------------------------------------------
        # デバッグ用：Yキー(緑色一斉包囲), Uキー(水色の帯状大群)
        # ------------------------------------------------------------
        if pyxel.btnp(pyxel.KEY_Y):
            # 大量の緑色で包囲する
            self.spawn_green_ring(num_enemies=20, distance=150)

        if pyxel.btnp(pyxel.KEY_U):
            # 水色の帯状大群を出現
            self.spawn_cyan_wave(num_enemies=30)  # 数はお好みで

        # ------------------------------------------------------------
        # レベルアップ判定：スコアに応じてレベルを更新し、敵の発生間隔を短縮
        #   (こちらはスコアを元にしたレベル概念)
        #   まとめて大量にスコアを得た場合に一気に複数レベル上昇するように while
        # ------------------------------------------------------------
        new_level = 1
        while self.score >= 5 * (new_level**2) + 15 * new_level:  # 5n^2+15n
            new_level += 1
        if new_level > self.level:
            self.level = new_level
            # レベルが上がるとスポーン間隔を短くする
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
        # 敵のスポーン処理（通常用：赤,青,緑のみ）
        # ------------------------------------------------------------
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0

        # ------------------------------------------------------------
        # 一定時間ごとのイベント管理
        #   30秒ごとに緑色の円形包囲
        #   45秒ごとに水色の帯状大群
        # ------------------------------------------------------------
        self.event_timer += 1

        # 30秒(1800フレーム)ごとに大量の緑色
        if self.event_timer % (60 * 30) == 0:
            self.spawn_green_ring(num_enemies=30, distance=150)

        # 45秒(2700フレーム)ごとに水色の帯状大群
        if self.event_timer % (60 * 45) == 0:
            self.spawn_cyan_wave(num_enemies=50)

        # ------------------------------------------------------------
        # 敵の移動や弾の発射、およびプレイヤーとの衝突判定
        # ------------------------------------------------------------
        for enemy in self.enemies[:]:
            if enemy['type'] in ['red', 'blue', 'green']:
                # 既存の処理：プレイヤーを追跡
                dx = self.player_x - enemy['x']
                dy = self.player_y - enemy['y']
                angle = math.atan2(dy, dx)
                
                if enemy['type'] == 'red':
                    # 赤い敵：プレイヤーに高速突進
                    enemy['x'] += math.cos(angle) * self.enemy_speed * 1.5
                    enemy['y'] += math.sin(angle) * self.enemy_speed * 1.5
                
                elif enemy['type'] == 'blue':
                    # 青い敵：ゆっくり移動 + 定期的に弾発射
                    enemy['x'] += math.cos(angle) * self.enemy_speed * 0.5
                    enemy['y'] += math.sin(angle) * self.enemy_speed * 0.5
                    enemy['shoot_timer'] += 1

                    # 1秒（60フレーム）ごとに弾を発射
                    if enemy['shoot_timer'] >= 60:
                        self.bullets.append({
                            'x': enemy['x'],
                            'y': enemy['y'],
                            'vx': math.cos(angle) * self.enemy_bullet_speed,
                            'vy': math.sin(angle) * self.enemy_bullet_speed,
                            'from_enemy': True
                        })
                        enemy['shoot_timer'] = 0
                
                else:  # 'green'
                    # 緑の敵：超低速で近づく
                    enemy['x'] += math.cos(angle) * self.enemy_speed * 0.2
                    enemy['y'] += math.sin(angle) * self.enemy_speed * 0.2

            elif enemy['type'] == 'cyan':
                # 水色の帯状大群：追跡はせず、最初に設定した速度で移動
                enemy['x'] += enemy['vx']
                enemy['y'] += enemy['vy']
            
            # プレイヤーと敵の衝突判定
            dist_pe = math.hypot(self.player_x - enemy['x'], self.player_y - enemy['y'])
            if dist_pe < self.player_size and not self.invincible:
                self.player_hp -= 3
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                
                # プレイヤーHPが0以下ならゲームオーバー
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.game_over = True
                    break
                
                # ダメージを受けたのでプレイヤーを無敵状態に
                self.invincible = True
                self.invincible_timer = 180  # 3秒相当（60FPS想定）

            # 画面外に出すぎたら削除（負荷軽減、特に水色の敵に有効）
            margin = 180
            screen_x = enemy['x'] - self.player_x + 128
            screen_y = enemy['y'] - self.player_y + 128
            if (screen_x < -margin or screen_x > 256 + margin or
                screen_y < -margin or screen_y > 256 + margin):
                if enemy in self.enemies:
                    self.enemies.remove(enemy)

        # ------------------------------------------------------------
        # 敵の弾とプレイヤーの衝突判定
        # ------------------------------------------------------------
        for bullet in self.bullets[:]:
            # 敵弾だけ衝突判定を行う
            if bullet.get('from_enemy', False):
                dist_pb = math.hypot(bullet['x'] - self.player_x, bullet['y'] - self.player_y)
                if dist_pb < self.player_size and not self.invincible:
                    self.player_hp -= 1
                    # HPが0以下でゲームオーバー
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
        # 電撃フィールドの効果
        # ------------------------------------------------------------
        if hasattr(self, 'electric_field') and self.electric_field:
            # チャージタイマーの更新
            if not self.electric_field_active:
                self.electric_field_cooldown -= 1
                if self.electric_field_cooldown <= 0:
                    self.electric_field_active = True

            # 電撃フィールドがアクティブな場合のみ効果を発揮
            if self.electric_field_active:
                enemy_hit = False
                for enemy in self.enemies[:]:
                    distance = math.hypot(self.player_x - enemy['x'], self.player_y - enemy['y'])
                    if distance < self.electric_field_radius:
                        # 敵にダメージを与える
                        enemy['hp'] = enemy.get('hp', 3) - self.electric_field_damage
                        if enemy['hp'] <= 0:
                            self.enemies.remove(enemy)
                            self.score += 1
                            # 経験値トークンを生成
                            self.exp_tokens.append({
                                'x': enemy['x'],
                                'y': enemy['y']
                            })
                            enemy_hit = True
                
                # 敵を倒した場合、60秒間のチャージを開始
                if enemy_hit:
                    self.electric_field_active = False
                    self.electric_field_cooldown = 60 * 60  # 60秒（60FPS）

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
        # マウスクリックでプレイヤー弾を発射
        # ------------------------------------------------------------
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.bullet_cooldown <= 0:
            dx = pyxel.mouse_x - 128
            dy = pyxel.mouse_y - 128
            angle = math.atan2(dy, dx)

            bullet_vx = math.cos(angle) * self.player_bullet_speed
            bullet_vy = math.sin(angle) * self.player_bullet_speed
            
            self.bullets.append({
                'x': self.player_x,
                'y': self.player_y,
                'vx': bullet_vx,
                'vy': bullet_vy,
                'from_enemy': False
            })
            
            # クールダウンを初期化
            self.bullet_cooldown = self.cooldown_time

        # ------------------------------------------------------------
        # 弾の更新 & 敵との衝突判定
        # ------------------------------------------------------------
        for bullet in self.bullets[:]:
            # 誘導弾の場合、最も近い敵を追尾
            if hasattr(self, 'homing_bullets') and self.homing_bullets and not bullet.get('from_enemy', False):
                nearest_enemy = None
                min_distance = float('inf')
                for enemy in self.enemies:
                    distance = math.hypot(bullet['x'] - enemy['x'], bullet['y'] - enemy['y'])
                    if distance < min_distance:
                        min_distance = distance
                        nearest_enemy = enemy
                
                if nearest_enemy:
                    dx = nearest_enemy['x'] - bullet['x']
                    dy = nearest_enemy['y'] - bullet['y']
                    angle = math.atan2(dy, dx)
                    bullet['vx'] = math.cos(angle) * self.homing_bullet_speed
                    bullet['vy'] = math.sin(angle) * self.homing_bullet_speed
            
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
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                            self.score += 1
                            # 経験値トークンを生成
                            self.exp_tokens.append({
                                'x': enemy['x'],
                                'y': enemy['y']
                            })
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
            
            # 一定距離(30ピクセル)以内なら吸い寄せ
            if distance < 30:
                angle = math.atan2(dy, dx)
                exp_token['x'] -= math.cos(angle) * self.exp_token_speed * 2
                exp_token['y'] -= math.sin(angle) * self.exp_token_speed * 2

            # プレイヤーとトークンの衝突判定
            if distance < self.player_size:
                self.exp_tokens.remove(exp_token)
                self.exp_count += 1

        # ------------------------------------------------------------
        # 「次のスキル取得に必要な経験値」を超えたかどうかをチェック
        # ------------------------------------------------------------
        if (self.exp_count >= self.next_skill_threshold
            and not self.show_skill_select):
            # 累計経験値が閾値を超えた「タイミング」で 1度だけスキル選択を表示
            self.show_skill_select = True
            self.paused = True
            self.generate_skill_options()

    def spawn_enemy(self):
        """
        一定距離離れた円周上に1体だけランダムなタイプの敵をスポーンさせる
        (赤,青,緑の3種のみ)
        """
        angle = random.uniform(0, math.pi * 2)
        spawn_radius = 180
        spawn_x = self.player_x + math.cos(angle) * spawn_radius
        spawn_y = self.player_y + math.sin(angle) * spawn_radius
        
        # 水色(cyan)は通常スポーンさせない
        enemy_type = random.choice(['red', 'blue', 'green'])
        
        self.enemies.append({
            'x': spawn_x,
            'y': spawn_y,
            'type': enemy_type,
            'shoot_timer': 0
        })

    def spawn_green_ring(self, num_enemies=8, distance=120):
        """
        緑色の敵を円形に大量配置して包囲させるイベント用のメソッド。
        """
        for i in range(num_enemies):
            angle = (2 * math.pi / num_enemies) * i
            spawn_x = self.player_x + math.cos(angle) * distance
            spawn_y = self.player_y + math.sin(angle) * distance
            self.enemies.append({
                'x': spawn_x,
                'y': spawn_y,
                'type': 'green',  # 緑色の敵
                'shoot_timer': 0
            })

    def spawn_cyan_wave(self, num_enemies=120):
        """
        プレイヤー方向へ向かうベクトルにランダムな角度を加え、
        全員が完全に一点に収束せず、ある程度拡散した帯になるようにする。
        """
        directions = ['top-right', 'top-left', 'bottom-right', 'bottom-left']
        direction = random.choice(directions)

        px, py = self.player_x, self.player_y

        base_dist = 180
        band_width_x = 120
        band_width_y = 80
        speed = 5

        if direction == 'top-right':
            spawn_base_x = px + base_dist
            spawn_base_y = py - base_dist
        elif direction == 'top-left':
            spawn_base_x = px - base_dist
            spawn_base_y = py - base_dist
        elif direction == 'bottom-right':
            spawn_base_x = px + base_dist
            spawn_base_y = py + base_dist
        else:
            spawn_base_x = px - base_dist
            spawn_base_y = py + base_dist

        for _ in range(num_enemies):
            # 帯として分散させるため、X/Yそれぞれにランダムオフセット
            offset_x = random.uniform(-band_width_x/2, band_width_x/2)
            offset_y = random.uniform(-band_width_y/2, band_width_y/2)

            sx = spawn_base_x + offset_x
            sy = spawn_base_y + offset_y

            # プレイヤーの位置 - スポーン位置
            dx = px - sx
            dy = py - sy
            base_angle = math.atan2(dy, dx)

            # ★ここでランダムな拡散角を加える（例：±0.2ラジアン ≈ ±11.5度）
            spread = random.uniform(-0.2, 0.2)  
            angle = base_angle + spread

            # 速度ベクトル
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            self.enemies.append({
                'x': sx,
                'y': sy,
                'type': 'cyan',
                'vx': vx,
                'vy': vy,
            })



    class Satellite:
        """
        衛星オブジェクト：プレイヤーの周囲を回転し、敵に衝突して倒す。
        """
        def __init__(self, player, index, total):
            self.player = player
            self.angle = (2 * math.pi / total) * index
            self.distance = 40
            self.speed = 0.05
            self.size = 2
            self.color = 9
            self.damage = 1

        def update(self):
            self.angle += self.speed
            if self.angle > math.pi * 2:
                self.angle -= math.pi * 2
            
            for enemy in self.player.enemies[:]:
                dist_se = math.hypot(self.get_x() - enemy['x'], self.get_y() - enemy['y'])
                if dist_se < self.size + self.player.enemy_size:
                    self.player.enemies.remove(enemy)
                    self.player.score += 1
                    self.player.exp_tokens.append({
                        'x': enemy['x'],
                        'y': enemy['y']
                    })

        def get_x(self):
            return self.player.player_x + math.cos(self.angle) * self.distance

        def get_y(self):
            return self.player.player_y + math.sin(self.angle) * self.distance

        def draw(self):
            screen_x = self.get_x() - self.player.player_x + 128
            screen_y = self.get_y() - self.player.player_y + 128
            pyxel.circ(screen_x, screen_y, self.size, self.color)

    def add_satellite(self):
        """
        衛星を追加し、既存の衛星を等間隔に再配置する
        """
        total = len(self.satellites) + 1
        for i, satellite in enumerate(self.satellites):
            satellite.angle = (2 * math.pi / total) * i
        self.satellites.append(self.Satellite(self, len(self.satellites), total))

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
        
        # イベントタイマーをリセット
        self.event_timer = 0

        # スキル関連の状態をリセット
        if hasattr(self, 'has_homing_bullet'):
            del self.has_homing_bullet
        if hasattr(self, 'has_electric_field'):
            del self.has_electric_field
        if hasattr(self, 'homing_bullets'):
            del self.homing_bullets
        if hasattr(self, 'electric_field'):
            del self.electric_field

        # スキル取得管理用の変数も再初期化
        self.skill_level = 1
        self.next_skill_threshold = self.get_skill_threshold(self.skill_level)

    def add_homing_bullet(self):
        """
        誘導弾を追加する
        """
        self.homing_bullets = True
        self.homing_bullet_speed = 3
        self.has_homing_bullet = True

    def add_electric_field(self):
        """
        電撃フィールドを追加する
        """
        self.electric_field = True
        self.electric_field_active = True
        self.electric_field_radius = 20
        self.electric_field_damage = 1
        self.electric_field_cooldown = 0
        self.has_electric_field = True

    def generate_skill_options(self):
        """
        スキル選択画面に表示するスキル一覧を生成
        取得していないスキルからランダムに3つを選択
        """
        all_skills = [
            {
                'name': '衛星砲',
                'description': 'プレイヤーを周回する補助砲台を追加',
                'effect': lambda: self.add_satellite()
            },
            {
                'name': '攻撃速度アップ',
                'description': '弾の発射間隔がより短くなる',
                'effect': lambda: setattr(self, 'cooldown_time',
                                          max(self.min_cooldown, self.cooldown_time - 2))
            },
            {
                'name': 'HP全回復',
                'description': 'プレイヤーのHPを最大値まで回復',
                'effect': lambda: setattr(self, 'player_hp', self.max_hp)
            },
            {
                'name': '誘導弾',
                'description': '発射した弾が敵を自動追尾する',
                'effect': lambda: self.add_homing_bullet(),
                'condition': lambda: not hasattr(self, 'has_homing_bullet') or not self.has_homing_bullet
            },
            {
                'name': '電撃フィールド',
                'description': 'プレイヤーの周囲に電撃フィールドを展開',
                'effect': lambda: self.add_electric_field(),
                'condition': lambda: not hasattr(self, 'has_electric_field') or not self.has_electric_field
            }
        ]
        
        available_skills = [
            skill for skill in all_skills
            if 'condition' not in skill or skill['condition']()
        ]
        
        # 利用可能なスキルからランダムに3つを選択
        self.skill_options = random.sample(available_skills, min(3, len(available_skills)))

    def draw(self):
        """
        メインの描画メソッド。Pyxel はここを1フレームごとに呼び出す。
        """
        pyxel.cls(0)

        # 背景ドット
        for x in range(-256, 256, 16):
            for y in range(-256, 256, 16):
                screen_x = (x - self.player_x) % 256
                screen_y = (y - self.player_y) % 256
                pyxel.pset(screen_x, screen_y, 3)

        # ゲームオーバー画面
        if self.game_over:
            game_over_text = "GAME OVER"
            text_width = len(game_over_text) * 4
            pyxel.text(128 - text_width // 2, 116, game_over_text, 7)
            
            restart_text = "Press 'R' to restart"
            text_width = len(restart_text) * 4
            pyxel.text(128 - text_width // 2, 132, restart_text, 7)
            
            score_text = f"Score: {self.score}"
            text_width = len(score_text) * 4
            pyxel.text(128 - text_width // 2, 148, score_text, 7)
            return

        # プレイヤー（画面中央に固定）
        screen_x = 128
        screen_y = 128
        if not self.invincible or (self.blink_timer // 10) % 2 == 0:
            pyxel.circ(screen_x, screen_y, self.player_size // 2, 7)

        # HPゲージ
        gauge_width = 20
        gauge_height = 3
        gauge_x = screen_x - gauge_width // 2
        gauge_y = screen_y + self.player_size // 2 + 5
        pyxel.rect(gauge_x, gauge_y, gauge_width, gauge_height, 1)
        hp_width = int(gauge_width * (self.player_hp / self.max_hp))
        pyxel.rect(gauge_x, gauge_y, hp_width, gauge_height, 8)

        # 敵を描画
        for enemy in self.enemies:
            ex = enemy['x'] - self.player_x + 128
            ey = enemy['y'] - self.player_y + 128
            # 色分け
            if enemy['type'] == 'red':
                color = 8
            elif enemy['type'] == 'blue':
                color = 12
            elif enemy['type'] == 'green':
                color = 11
            elif enemy['type'] == 'cyan':
                color = 13  # 水色っぽい色
            else:
                color = 7  # fallback
                
            pyxel.rect(ex - self.enemy_size//2, ey - self.enemy_size//2,
                       self.enemy_size, self.enemy_size, color)

        # 弾を描画
        for bullet in self.bullets:
            bx = bullet['x'] - self.player_x + 128
            by = bullet['y'] - self.player_y + 128
            color = 12 if bullet.get('from_enemy', False) else 8
            pyxel.rect(bx - self.bullet_size//2, by - self.bullet_size//2,
                       self.bullet_size, self.bullet_size, color)

        # 経験値トークンを描画
        for exp_token in self.exp_tokens:
            tx = exp_token['x'] - self.player_x + 128
            ty = exp_token['y'] - self.player_y + 128
            pyxel.circ(tx, ty, self.exp_token_size, 10)

        # クロスヘア
        size = self.crosshair_size
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        pyxel.line(mx - size, my, mx + size, my, self.crosshair_color)
        pyxel.line(mx, my - size, mx, my + size, self.crosshair_color)

        # 弾再発射ゲージ
        if self.bullet_cooldown > 0:
            gauge_width = 20
            gauge_height = 3
            gauge_x = mx - gauge_width // 2
            gauge_y = my + size + 5
            pyxel.rect(gauge_x, gauge_y, gauge_width, gauge_height, 1)
            progress = 1 - (self.bullet_cooldown / self.cooldown_time)
            filled_width = int(gauge_width * progress)
            pyxel.rect(gauge_x, gauge_y, filled_width, gauge_height, 8)

        # 衛星を描画
        for satellite in self.satellites:
            satellite.draw()

        # 電撃フィールド
        if hasattr(self, 'electric_field') and self.electric_field:
            if self.electric_field_active:
                pyxel.circb(128, 128, self.electric_field_radius, 12)
                for _ in range(5):
                    angle = random.uniform(0, 2 * math.pi)
                    length = random.uniform(0, self.electric_field_radius)
                    x = 128 + math.cos(angle) * length
                    y = 128 + math.sin(angle) * length
                    pyxel.line(128, 128, x, y, 12)
            else:
                charge_percent = 1 - (self.electric_field_cooldown / (60 * 60))
                pyxel.circb(128, 128, self.electric_field_radius, 13)
                pyxel.text(120, 128, f"{int(charge_percent * 100)}%", 13)

        # UI系表示 (スコア・経験値など)
        pyxel.text(5, 5, f"X:{self.player_x:.1f} Y:{self.player_y:.1f}", 7)
        pyxel.text(5, 235, f"Score:{self.score} Exp:{self.exp_count}", 7)

        # スキル選択画面
        if self.show_skill_select:
            pyxel.rect(50, 50, 156, 156, 1)
            draw_text_with_border(80, 50, "スキルを選択", 7, 5, self.font)
            draw_text_with_border(60, 65, "1,2,3 キーで選択", 7, 5, self.font)
            for i, option in enumerate(self.skill_options):
                y = 90 + i * 35
                draw_text_with_border(60, y, f"{i+1}. {option['name']}", 7, 5, self.font)
                draw_text_with_border(60, y + 15, option['description'], 5, 1, self.font)


# アプリケーションを起動
App()
