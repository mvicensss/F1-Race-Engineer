import dgram from 'dgram';
import EventEmitter from 'events';
import PacketHeader from './parsers/PacketHeader';
import PacketSessionData from './parsers/PacketSessionData';
import PacketMotionData from './parsers/PacketMotionData';
import {
  MOTION,
  SESSION,
  LAP_DATA,
  EVENT,
  PARTICIPENTS,
  CAR_SETUPS,
  CAR_TELEMETRY,
  CAR_STATUS,
  PACKET_TYPES,
} from './constants/packetTypes';

import WebSocket from 'ws';

//start ws server at port 8080
const wss = new WebSocket.Server({ port: 8080 });

//setup connection
wss.on('connection', function connection(ws) {
  console.log('Python client connected to WebSocket server');
})
/**
 *
 */
class F12018UDP extends EventEmitter {
  constructor(opts = {}) {
    super(opts);
    const {
      port = 20777,
    } = opts;

    this.port = port;
    this.client = dgram.createSocket('udp4');
  }

  /**
   *
   * @param {Buffer} buffer
   */
  static parsePacketHeader(buffer) {
    const ph = new PacketHeader();
    return ph.fromBuffer(buffer);
  }

  /**
   *
   * @param {Number} packetId
   */
  static getParserByPacketId(packetId) {
    if (packetId === SESSION) {
      return PacketSessionData;
    }

    if (packetId === MOTION) {
      return PacketMotionData;
    }

    if (packetId === LAP_DATA) {
      return null;
    }

    if (packetId === EVENT) {
      return null;
    }

    if (packetId === PARTICIPENTS) {
      return null;
    }

    if (packetId === CAR_SETUPS) {
      return null;
    }

    if (packetId === CAR_TELEMETRY) {
      return null;
    }

    if (packetId === CAR_STATUS) {
      return null;
    }

    return null;
  }

  /**
   *
   * @param {Buffer} message
   */
  parseMessage(message) {
    const buffer = Buffer.from(message.buffer);

    const { m_packetId } = F12018UDP.parsePacketHeader(buffer); // eslint-disable-line
    const Parser = F12018UDP.getParserByPacketId(m_packetId);

    if (Parser !== null) {
      const packetData = new Parser(buffer);
      this.emit(PACKET_TYPES[m_packetId], packetData.data);

      //broadcast via websocket
      const payload = JSON.stringify({
        type: PACKET_TYPES[m_packetId],
        data: packetData.data
      });

      //iterate through all connected clients and send the payload
      wss.clients.forEach(function each(client) {
        if (client.readyState === WebSocket.OPEN) {
          client.send(payload);
        }
      });
    }
  }

  /**
   * Method to start listening for packets
   */
  start() {
    this.client.on('listening', () => {
      const address = this.client.address();
      console.log(`UDP Client listening on ${address.address}:${address.port}`);
      this.client.setBroadcast(true);
    });

    this.client.on('message', m => this.parseMessage(m));
    this.client.bind(this.port);
  }

  /**
   * Method to close the client
   */
  stop() {
    return this.client.close();
  }
}

export default F12018UDP;

const collector = new F12018UDP();
collector.start();
