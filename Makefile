TARGETS=install test

all: $(TARGETS)

install:

    @curl -sLO http://d2aly1rinbxnx9.cloudfront.net/RLBotGUI_1.0.exe
    @chmod +x RLBotGUI_1.0.exe
    @echo "RLBot GUI downloaded. This requires Windows and a copy of Rocket League."

test:

    @echo "Running unit tests..."

clean:
    
    @echo "Removing RLBot GUI..."
    @rm -f RLBotGUI_1.0.exe
