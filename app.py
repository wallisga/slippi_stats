file is executed directly
if __name__ == '__main__':
    # Create templates directory if running standalone
    os.makedirs('templates', exist_ok=True)
    # Start the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)