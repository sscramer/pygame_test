import pyxel
import math
import random

class App:
    def __init__(self):
        # ゲームウィンドウを初期化（幅256px、高さ256px）
        pyxel.init(256, 256, title="My Pyxel Game")
        
        # プレイヤーの初期状態を設定
        self.player_x = 0  # マップ上の位置
        self.player_y = 0
        self.player_size = 8
        self.player_speed = 2
        
        # 弾の状態を管理するリスト
        self.bullets = []
        self.bullet_speed = 4
        self.bullet_size = 2
        
        # 敵の状態を管理するリスト
        self.enemies = []
        self.enemy_size = 8
        self.enemy_speed = 1.5
        self.spawn_interval = 30
        self.spawn_timer = 0
        
        # クロスヘアの設定
        self.crosshair_size = 5
        self.crosshair_color = 8  # 赤色
        
        # ゲームの状態を管理する変数
        self.game_over = False
        
        # ゲームを開始
        pyxel.run(self.update, self.draw)
    
    def spawn_enemy(self):
        # ランダムな角度を生成（0-360度）
        angle = random.uniform(0, math.pi * 2)
        
        # スポーン位置（プレイヤーから離れた位置）
        spawn_radius = 180
        spawn_x = self.player_x + math.cos(angle) * spawn_radius
        spawn_y = self.player_y + math.sin(angle) * spawn_radius
        
        # 敵をリストに追加
        self.enemies.append({
            'x': spawn_x,
            'y': spawn_y,
            'angle': angle
        })
    
    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.game_over = False
                self.reset_game()
            return

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
            # プレイヤーの方向へ移動
            dx = self.player_x - enemy['x']
            dy = self.player_y - enemy['y']
            angle = math.atan2(dy, dx)
            enemy['x'] += math.cos(angle) * self.enemy_speed
            enemy['y'] += math.sin(angle) * self.enemy_speed
            
            # プレイヤーと敵の衝突判定
            if math.sqrt(dx * dx + dy * dy) < self.player_size:
                self.game_over = True
                break
        
        # マウスクリックで弾を発射
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
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
            
            # 弾と敵の衝突判定
            for enemy in self.enemies[:]:
                dx = bullet['x'] - enemy['x']
                dy = bullet['y'] - enemy['y']
                if math.sqrt(dx * dx + dy * dy) < self.enemy_size:
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
    
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
            pyxel.circ(screen_x, screen_y, self.player_size // 2, 7)
            
            # 敵を描画
            for enemy in self.enemies:
                screen_x = enemy['x'] - self.player_x + 128
                screen_y = enemy['y'] - self.player_y + 128
                pyxel.rect(screen_x - self.enemy_size//2, screen_y - self.enemy_size//2, 
                          self.enemy_size, self.enemy_size, 8)
            
            # 弾を描画
            for bullet in self.bullets:
                screen_x = bullet['x'] - self.player_x + 128
                screen_y = bullet['y'] - self.player_y + 128
                pyxel.rect(screen_x - self.bullet_size//2, screen_y - self.bullet_size//2, 
                           self.bullet_size, self.bullet_size, 10)
            
            # クロスヘアを描画
            size = self.crosshair_size
            x = pyxel.mouse_x
            y = pyxel.mouse_y
            pyxel.line(x - size, y, x + size, y, self.crosshair_color)
            pyxel.line(x, y - size, x, y + size, self.crosshair_color)

        # デバッグ用にプレイヤーの座標を表示
        pyxel.text(5, 5, f"X: {self.player_x:.1f}, Y: {self.player_y:.1f}", 7)

    def reset_game(self):
        # プレイヤーの初期状態を設定
        self.player_x = 0
        self.player_y = 0
        
        # 弾の状態を管理するリストを初期化
        self.bullets = []
        
        # 敵の状態を管理するリストを初期化
        self.enemies = []
        self.spawn_timer = 0

if __name__ == "__main__":
    App()