deploy:
	pyboard --device /dev/tty.usbmodem0000000000001 -f cp dht.py :
	pyboard --device /dev/tty.usbmodem0000000000001 -f cp main.py :

clear:
	pyboard --device /dev/tty.usbmodem0000000000001 -f rm dht.py
	pyboard --device /dev/tty.usbmodem0000000000001 -f rm main.py

run: deploy
	pyboard --device /dev/tty.usbmodem0000000000001 main.py
