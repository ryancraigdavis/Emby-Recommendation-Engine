#!/bin/bash

echo "🧪 Testing Docker Compose Services with Web UIs..."
echo "================================================="

echo "📊 Container Status:"
docker compose ps

echo ""
echo "🐘 Testing PostgreSQL..."
if docker compose exec -T postgres pg_isready -U postgres; then
    echo "✅ PostgreSQL is ready"
    echo "   📱 PgAdmin: http://localhost:5050"
else
    echo "❌ PostgreSQL failed"
fi

echo ""
echo "🔴 Testing Redis..."
if docker compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is working"
    echo "   📱 Redis Commander: http://localhost:8081"
else
    echo "❌ Redis failed"
fi

echo ""
echo "📨 Testing Kafka..."
if docker compose exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list >/dev/null 2>&1; then
    echo "✅ Kafka is working"
    echo "   📱 Kafka UI: http://localhost:8080"
else
    echo "❌ Kafka failed"
fi

echo ""
echo "🦓 Testing Zookeeper..."
if docker compose exec -T zookeeper zkCli.sh -server localhost:2181 <<< "ls /" | grep -q "zookeeper" 2>/dev/null; then
    echo "✅ Zookeeper is working"
else
    echo "❌ Zookeeper failed"
fi

echo ""
echo "🌐 Host machine connectivity:"
echo "PostgreSQL: $(nc -z localhost 5432 && echo "✅" || echo "❌")"
echo "Redis: $(nc -z localhost 6379 && echo "✅" || echo "❌")"
echo "Kafka: $(nc -z localhost 9092 && echo "✅" || echo "❌")"
echo "Zookeeper: $(nc -z localhost 2181 && echo "✅" || echo "❌")"

echo ""
echo "🎉 Web Admin Interfaces:"
echo "📊 PgAdmin (PostgreSQL): http://localhost:5050"
echo "📊 Redis Commander: http://localhost:8081" 
echo "📊 Kafka UI: http://localhost:8080"
echo ""
echo "Login credentials saved above! 👆"
