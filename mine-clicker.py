from enum import Enum
import json
import pathlib
import pygame
import random
import typing

pygame.init()

# Звук при клике
def sound(number: int) -> None:
	if number == 0:
		sound_1.play()
	elif number == 1:
		sound_2.play()
	elif number == 2:
		sound_3.play()
	else:
		sound_4.play()

# Цвета
class Color(tuple, Enum):
	RED: tuple = (255, 0, 0)
	WHITE: tuple = (255, 255, 255)

# Путь до папки с файлами: текстур, музыки и т.д.
data_path = pathlib.Path.cwd() / "data"


# Класс ресурсов
class Resources:
	def __init__(self):
		# загрузка настраиваемой конфигурации
		with open(data_path / "config.json", "r") as config_file:
			config = json.load(config_file)

		self.current_pickaxe_id: int = 0                                       # текущий номер кирки
		self.diamonds_count: int = config["diamonds count"]                    # Количество алмазов
		self.diamonds_grow_per_click: int = config["diamonds grow per click"]  # Прирост алмазов за клик
		self.diamonds_grow_auto: int = config["diamonds grow auto"]            # Автоматический прирост алмазов

		self.upgrade_info: list = [] # стоимость улучшения кирки и новый доход
		for i in range(0, len(config["upgrade info"])):
			self.upgrade_info.append([config["upgrade info"][i]["cost"], config["upgrade info"][i]["diamonds grow"]])

		# стоимость покупки стива и его доход
		self.buy_steve_info: list = [config["buy steve info"][0]["cost"], config["buy steve info"][0]["diamonds grow"]]

	# Увеличение числа алмазов за клик
	def inc_diamonds(self) -> None:
		self.diamonds_count += self.diamonds_grow_per_click

	# Автоматическое увеличение числа алмазов
	def auto_add_diamonds(self) -> None:
		self.diamonds_count += self.diamonds_grow_auto

	# Улучшение кирки
	def upgrade(self) -> None:
		if self.current_pickaxe_id < len(self.upgrade_info) and self.diamonds_count >= self.upgrade_info[self.current_pickaxe_id][0]:
			pickaxe_sound.play()
			self.diamonds_count -= self.upgrade_info[self.current_pickaxe_id][0]
			self.diamonds_grow_per_click = self.upgrade_info[self.current_pickaxe_id][1]
			self.current_pickaxe_id += 1

	# Добавить Стива
	def add_steve(self) -> None:
		if self.diamonds_count >= self.buy_steve_info[0]:
			steve_sound.play()
			self.diamonds_count -= self.buy_steve_info[0]
			self.diamonds_grow_auto += self.buy_steve_info[1]


# Класс окно приложения
class Window:
	width: int = 1280 # ширина окна
	height: int  = 720 # высота окна

	game = pygame.display.set_mode((width, height))
	draw_screen = pygame.Surface((width, height))

	# Шрифты для текста
	big_font = pygame.font.Font(data_path / "font.ttf", 50)
	medium_font = pygame.font.Font(data_path / "font.ttf", 25)
	small_font = pygame.font.Font(data_path / "font.ttf", 10)

	# Изображение для заднего плана
	background_image = pygame.image.load(data_path / "background_image.jpg").convert()

	# Изображение алмаза
	diamond_image = pygame.image.load(data_path / "diamond.png").convert()

	# Изображение кирок
	pickaxes: list = [pygame.image.load(data_path / "wooden_pickaxe.png").convert(),
					  pygame.image.load(data_path / "stone_pickaxe.png").convert(),
					  pygame.image.load(data_path / "iron_pickaxe.png").convert(),
					  pygame.image.load(data_path / "golden_pickaxe.png").convert(),
					  pygame.image.load(data_path / "diamond_pickaxe.png").convert(),
					  pygame.image.load(data_path / "netherite_pickaxe.png").convert()]

	# Кнопка для кликания - с изображением руды
	click_button = pygame.draw.rect(draw_screen, Color.WHITE, pygame.Rect(430, 150, 420, 420))
	ore_image = pygame.image.load(data_path / "diamond_ore.png").convert()

	# Кнопка улучшения кирки
	upgrade_pickaxe_button = pygame.draw.rect(draw_screen, Color.WHITE, pygame.Rect(900, 150, 350, 100))
	upgrade_pickaxe = medium_font.render("Upgrade pickaxe", 1, Color.RED)

	# Информация для улучшения кирки
	upgrade_info: list = ["Wooden --> Stone, {0} diamonds, {1} diamonds per click",
						  "Stone --> Iron, {0} diamonds, {1} diamonds per click",
						  "Iron --> Gold, {0} diamonds, {1} diamonds per click", 
						  "Gold --> Diamond, {0} diamonds, {1} diamonds per click",
						  "Diamond --> Netherite, {0} diamonds, {1} diamonds per click"]

	# Кнопка для покупки Стива - автокликера
	buy_steve_button = pygame.draw.rect(draw_screen, Color.WHITE, pygame.Rect(900, 470, 350, 100))
	buy_steve = medium_font.render("Buy Steve - slave", 1, Color.RED)

	# Информация о покупке Стива
	buy_steve_info: str = "Steve mine {0} diamonds in auto regime, {1} diamonds"

	# Счетчик и информация о приросте алмазов
	diamonds_counter = big_font.render("Your diamonds: ", 1, Color.RED)
	diamonds_grow_info = medium_font.render("Diamonds per click: ", 1, Color.RED)
	diamonds_auto_grow_info = medium_font.render("Diamonds per second: ", 1, Color.RED)

	def __init__(self):
		pass

	# Обновление окна
	def update(self, res: Resources) -> None:
		# фоновое изображение
		self.draw_screen.blit(self.background_image, (0, 0))

		# фон кнопки для кликанья
		self.click_button = pygame.draw.rect(self.draw_screen, Color.WHITE, pygame.Rect(430, 150, 420, 420))

		# кнопка обновления кирки
		if (res.current_pickaxe_id < len(res.upgrade_info)):
			self.upgrade_pickaxe_button = pygame.draw.rect(self.draw_screen, Color.WHITE, pygame.Rect(900, 150, 350, 100))
			self.draw_screen.blit(self.upgrade_pickaxe, (950, 185))
			upgrade_info = self.small_font.render(self.upgrade_info[res.current_pickaxe_id].format(*res.upgrade_info[res.current_pickaxe_id]), 1, Color.RED)
			self.draw_screen.blit(upgrade_info, (910, 230))

		# кнопка покупки Стива
		self.buy_steve_button = pygame.draw.rect(self.draw_screen, Color.WHITE, pygame.Rect(900, 470, 350, 100))
		self.draw_screen.blit(self.buy_steve, (945, 505))
		buy_steve_info = self.small_font.render(self.buy_steve_info.format(res.buy_steve_info[1], res.buy_steve_info[0]), 1, Color.RED)
		self.draw_screen.blit(buy_steve_info, (915, 550))

		# изображение кнопки для клика
		self.draw_screen.blit(self.ore_image, (440, 160))
		# изображение кирки
		self.draw_screen.blit(self.pickaxes[res.current_pickaxe_id], (560, 560))

		# счетчик алмазов
		self.draw_screen.blit(pygame.transform.scale(self.diamond_image, (self.diamond_image.get_width() // 4, self.diamond_image.get_height() // 4)), (5, 5))
		self.draw_screen.blit(self.diamonds_counter, (50, 5))
		diamonds_counter_count = self.big_font.render("{}".format(res.diamonds_count), 1, Color.RED)
		self.draw_screen.blit(diamonds_counter_count, (530, 5))

		# информация о текущем приросте за клик
		self.draw_screen.blit(self.diamonds_grow_info, (5, 150))
		diamonds_grow_count = self.medium_font.render("{}".format(res.diamonds_grow_per_click), 1, Color.RED)
		self.draw_screen.blit(diamonds_grow_count, (315, 150))

		# информация о текущем автоматическом приросте
		self.draw_screen.blit(self.diamonds_auto_grow_info, (5, 190))
		diamonds_grow_auto = self.medium_font.render("{}".format(res.diamonds_grow_auto), 1, Color.RED)
		self.draw_screen.blit(diamonds_grow_auto, (350, 190))        

		self.game.blit(self.draw_screen, (0, 0))

		pygame.display.flip()


# Класс игра
class Game(object):
	window: Window = Window() # окно игры
	res: Resources = Resources() # ресурсы

	timer: int = 1000 # таймер для автоматического прироста

	def __init__(self):
		pygame.display.set_caption("Mine Clicker by NikEvKuz")

	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(Game, cls).__new__(cls)
		return cls.instance

	# Процесс игры
	def play_game(self) -> None:
		pygame.time.set_timer(auto_grow_event, self.timer)

		# Event-loop
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT: # выход из игры
					pygame.quit()
					exit()
				elif event.type == pygame.KEYDOWN: # нажата клавиша
					if event.key == pygame.K_SPACE: # пробел
						sound(random.randint(0, 3))
						self.res.inc_diamonds()
				elif event.type == auto_grow_event: # автоматическое увеличение алмазов
					self.res.auto_add_diamonds()
				elif event.type == pygame.MOUSEBUTTONDOWN: # клик мышкой
					left_button = pygame.mouse.get_pressed()
					mouse_x, mouse_y = pygame.mouse.get_pos()

					if self.window.click_button.collidepoint(mouse_x, mouse_y): # клик по руде
						sound(random.randint(0, 3))
						self.res.inc_diamonds()
					if self.window.upgrade_pickaxe_button.collidepoint(mouse_x, mouse_y): # клик по улучшению кирки
						self.res.upgrade()
					if self.window.buy_steve_button.collidepoint(mouse_x, mouse_y): # клик по покупке Стива
						self.res.add_steve()

			self.window.update(self.res)


if  __name__ == "__main__":
	# Загружаем музыку на фон
	pygame.mixer.music.load(data_path / "soundtrack.ogg")
	pygame.mixer.music.play(-1)

	# Загрузка игровых звуков
	sound_1 = pygame.mixer.Sound(data_path / "sound_1.ogg")
	sound_2 = pygame.mixer.Sound(data_path / "sound_2.ogg")
	sound_3 = pygame.mixer.Sound(data_path / "sound_3.ogg")
	sound_4 = pygame.mixer.Sound(data_path / "sound_4.ogg")
	pickaxe_sound = pygame.mixer.Sound(data_path / "upgrade_pickaxe.ogg")
	steve_sound = pygame.mixer.Sound(data_path / "steve.ogg")

	# Объявление пользовательского ивента - автоматический прирост алмазов
	auto_grow_event = pygame.USEREVENT + 1

	game = Game()
	game.play_game()
