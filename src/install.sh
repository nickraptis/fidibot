#!/usr/bin/env bash

FIDIBOT_STRINGS_DIR="../../fidibot-strings"

if [ "$1" == "update" ]
then
	git pull

	if [ -d $FIDIBOT_STRINGS_DIR ]
	then
		pushd $FIDIBOT_STRINGS_DIR
		git pull
		popd
	fi
fi

pip install -r ../requirements.pip

if [ ! -d log ]
then
	mkdir log
fi

if [ ! -d log/moolog ]
then
	mkdir log/moolog
fi

if [ ! -d alternatives ]
then
	if [ -d $FIDIBOT_STRINGS_DIR ]
	then
		ln -s "$FIDIBOT_STRINGS_DIR/alternatives" alternatives
	else
		mkdir alternatives
	fi
fi

