#!/usr/bin/env bash

if [ -f config ]
then
	source config
else
	source config.sample
fi

FIDI_COMMAND="python fidibot.py"

if [[ "$FIDI_PASSWORD" != "" ]]
then
	FIDI_COMMAND+=" -x \"$FIDI_PASSWORD\""
fi

if [[ "$FIDI_REALNAME" != "" ]]
then
	FIDI_COMMAND+=" -r \"$FIDI_REALNAME\""
fi

if [[ "$FIDI_PORT" != "" ]]
then
	FIDI_COMMAND+=" -p $FIDI_PORT"
fi

FIDI_COMMAND+=" $FIDI_SERVER $FIDI_CHANNEL $FIDI_USERNAME $@"

echo $FIDI_COMMAND
eval $FIDI_COMMAND

