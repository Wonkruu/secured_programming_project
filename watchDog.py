#! /usr/bin/env python3
# _*_ coding: utf8 _*_
import os
import socket
import sys
import time

from action import createdSharedMemory
from primaryServer import primaryServerBehavior
from secondaryServer import secondaryServerBehavior


def launchWatchDog():
    host = '127.0.0.1'
    primaryServerPort = 1111
    secondaryServerPort = 2222

    pathTube1 = "/tmp/tubenommeprincipalsecond.fifo"
    pathTube2 = "/tmp/tubenommesecondprincipal.fifo"

    name = "leclerc"
    create = True
    size = 10

    sharedMemory = createdSharedMemory(name, create, size)

    launchPrimaryServer(sharedMemory, pathTube1, pathTube2, host, primaryServerPort)
    launchSecondaryServer(sharedMemory, pathTube1, pathTube2, host, secondaryServerPort)


def launchPrimaryServer(sharedMemory, pathTube1, pathTube2, host, port):
    newPid = os.fork()

    if newPid < 0:
        print("WatchDog> fork impossible")
        os.abort()
    elif newPid == 0:
        openWatchDogConnection(host, port)
    else:
        linkToWatchDog(host, port)
        primaryServerBehavior(sharedMemory, pathTube1, pathTube2)
        sys.exit(0)


def launchSecondaryServer(sharedMemory, pathTube1, pathTube2, host, port):
    newPid = os.fork()

    if newPid < 0:
        print("Server> fork impossible")
        os.abort()
    elif newPid == 0:
        openWatchDogConnection(host, port)
    else:
        linkToWatchDog(host, port)
        secondaryServerBehavior(sharedMemory, pathTube1, pathTube2, host, port)


def openWatchDogConnection(host, port):
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        mySocket.bind((host, port))
    except socket.error:
        print('\nWatch dog> Impossible d\'établir la liaison du socket à l\'adresse choisie ({}:{})\n'.format(host, port))
        sys.exit()

    while True:
        print('Watch dog prêt, en attente de requêtes sur {}:{}'.format(host, port))
        mySocket.listen(5)

        connexion, address = mySocket.accept()
        print('Client connecté, adresse IP %s, port %s' % (address[0], address[1]))

        connexion.send(bytes('Connected to server', 'UTF-8'))
        while True:
            msgClientraw = connexion.recv(1024)
            msgClient = msgClientraw.decode('UTF-8')
            print('watch dog>', msgClient)
            if msgClient.upper() == "FIN":
                break
            msgServeur = bytes('Server> Connexion ok', 'UTF-8')
            connexion.send(msgServeur)
            time.sleep(2)

        connexion.send(bytes('Fin de connexion !', 'UTF-8'))
        print('Connexion interrompue.')
        connexion.close()
        break

    mySocket.close()
    del mySocket


def linkToWatchDog(host, port):
    time.sleep(5)
    attempt = 0
    cpt = 0
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while attempt < 5:
        try:
            attempt += 1
            mySocket.connect((host, port))
            break
        except socket.error:
            print("\nServer> Connexion au serveur impossible à {}:{} !\n".format(host, port))
            if attempt >= 5:
                sys.exit()
            time.sleep(2)
    print("Server> Connexion établie avec le serveur de test ({}:{}).".format(host, port))

    msgServeurraw = mySocket.recv(1024)
    msgServeur = msgServeurraw.decode('UTF-8')

    while True:
        if msgServeur.upper() == "FIN":
            break
        print("ServeurParent>", msgServeur)

        if (cpt < 3):
            msgClient = bytes('Connexion watch ok', 'UTF-8')
            cpt += 1
            mySocket.send(msgClient)
            time.sleep(2)
        else:
            msgClient = bytes('FIN', 'UTF-8')
            mySocket.send(msgClient)
            break
    # while True:
    #     print('Serveur prêt, en attente de requêtes sur {}:{}...'.format(host, port))
    #     mySocket.listen(5)
    #
    #     connexion, adresse = mySocket.accept()
    #     print('Client connecté, adresse IP %s, port %s' % (adresse[0], adresse[1]))
    #     print('Tapez le mot FIN pour terminer.')
    #
    #     connexion.send(bytes(
    #         'Vous etes connecte au serveur de test. Envoyez vos messages (sur une ligne) ou le mot FIN pour terminer.',
    #         'UTF-8'))
    #
    #     while True:
    #         msgClientraw = connexion.recv(1024)
    #         msgClient = msgClientraw.decode('UTF-8')
    #         print('Client>', msgClient)
    #         if msgClient.upper() == 'FIN' or msgClient == '':
    #             break
    #         msgServeur = bytes(input('Serveur> '), 'UTF-8')
    #         connexion.send(msgServeur)
    #
    #     connexion.send(bytes('Fin de connexion !', 'UTF-8'))
    #     print('Connexion interrompue.')
    #     connexion.close()
    #
    #     ch = input('<R>ecommencer <T>erminer ? ')
    #     if ch.upper() == 'T':
    #         break

    print("Connexion interrompue. Watchdog")
    time.sleep(2)
    mySocket.close()
    del mySocket

