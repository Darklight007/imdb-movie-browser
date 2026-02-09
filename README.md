# 🎬 IMDB Movie Browser

A free, fast, and beautiful web application for searching and exploring movies from the IMDB dataset.

![License](https://img.shields.io/badge/license-Non--Commercial-yellow)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Flask](https://img.shields.io/badge/flask-3.0-green)

**Created by Homayoun Jamshidi** | [GitHub](https://github.com/Darklight007)

> This project was designed and directed by Homayoun Jamshidi. All features, user experience, and functionality decisions were conceived by the creator. Implementation assisted by Claude Code.

## ✨ Features

- 🔍 **Advanced Search** - Filter by title, director, cast, year, rating, votes
- 🎭 **Genre Filtering** - Select multiple genres with AND/OR logic
- 🌍 **Language & Country** - Filter by original language and country of origin
- ⭐ **Smart Sorting** - Sort by rating, popularity, year, or title
- 📱 **Responsive Design** - Works beautifully on desktop, tablet, and mobile
- ⚡ **Lightning Fast** - Optimized SQLite with indexes and caching
- 🎨 **Clean UI** - Modern, intuitive interface inspired by IMDB

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- IMDB dataset (see setup instructions)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/imdb-movie-browser.git
cd imdb-movie-browser

# Install dependencies
pip install -r requirements.txt

# Copy your database file
cp /path/to/imdb_dataset.db ./

# Run the application
python3 app.py
```

Visit: **http://localhost:5000**

## 📊 Database Setup

This application requires the IMDB SQLite database. To create it:

```bash
# From the parent directory containing the desktop GUI
cd ..

# Option 1: Download fresh data (recommended)
python3 download_imdb_data_auto.py  # ~10 minutes
python3 convert_to_sqlite.py         # ~2-3 minutes

# Option 2: Fix existing data
python3 fix_country_data.py          # ~3-5 minutes
python3 convert_to_sqlite.py         # ~2-3 minutes

# Copy to web app directory
cp imdb_dataset.db imdb_web_app/
```

## 🌐 Deployment

Deploy to the cloud for free!

### Render.com (Recommended)

```bash
# Push to GitHub
git add .
git commit -m "Initial commit"
git push origin main

# Deploy on Render
1. Go to https://render.com
2. Connect your GitHub repo
3. Render auto-detects configuration
4. Click "Create Web Service"
5. Done! 🎉
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions including Railway and PythonAnywhere.

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture and code structure
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide for Render, Railway, PythonAnywhere
- **[GITHUB_SETUP.md](GITHUB_SETUP.md)** - Step-by-step GitHub repository setup

## 🎯 Use Cases

- **Movie Discovery** - Find hidden gems based on your preferences
- **Research** - Analyze movie trends by year, genre, country
- **Education** - Learn about cinema from different eras and regions
- **Portfolio** - Showcase your web development skills

## 🖼️ Screenshots

### Search Interface
![Search Page](https://via.placeholder.com/800x500?text=Search+Interface)

### Movie Details
![Movie Detail](https://via.placeholder.com/800x500?text=Movie+Detail+Page)

### Mobile Responsive
![Mobile View](https://via.placeholder.com/400x600?text=Mobile+View)

## 🔧 Technology Stack

- **Backend:** Python 3.11, Flask 3.0
- **Database:** SQLite with WAL mode
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Server:** Gunicorn WSGI
- **Hosting:** Render.com (or Railway, PythonAnywhere)

## 📈 Performance

- **Database Size:** ~75MB (300K+ movies)
- **Query Speed:** <50ms average
- **Page Load:** <2 seconds
- **Optimizations:**
  - 7 database indexes
  - 64MB query cache
  - Memory-mapped I/O
  - Efficient query building

## ⚖️ License & Attribution

This project uses data from **IMDB's Non-Commercial Datasets**.

**Information courtesy of [IMDb](https://www.imdb.com). Used with permission.**

### Usage Terms

✅ **Allowed:**
- Personal use
- Educational projects
- Portfolio/resume showcase
- Free public access

❌ **Not Allowed:**
- Commercial use (ads, subscriptions)
- Data redistribution
- Creating competing services

For commercial licensing, contact: **licensing@imdb.com**

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues

- Search results limited to 500 movies (configurable)
- Free hosting may sleep after inactivity
- Some older movies missing country data

## 🗺️ Roadmap

- [ ] User accounts and watchlists
- [ ] Movie recommendations
- [ ] Advanced statistics and charts
- [ ] Export search results (CSV/JSON)
- [ ] Full-text search
- [ ] Pagination for large result sets
- [ ] Movie posters (if IMDB API available)

## 💡 Tips

- Use wildcards in search: `*Nolan*` matches "Christopher Nolan"
- Combine filters: Genre=Drama + Rating≥8.0 + Votes≥10K
- Click column headers to sort results
- Mobile users: Swipe right on tables to see more columns

## 🙋 FAQ

**Q: Can I use this commercially?**
A: No, IMDB data is for non-commercial use only. Contact IMDB for commercial licensing.

**Q: How often is data updated?**
A: You need to manually re-download IMDB datasets (they update daily).

**Q: Why are some movies missing?**
A: Only movies with ratings and complete metadata are included.

**Q: Can I add movie posters?**
A: Not with the free datasets. IMDB's API requires separate licensing.

**Q: What about TV shows?**
A: Currently movies only. TV shows can be added by modifying the data download script.

## 📧 Contact

For questions about:
- **IMDB Data:** imdb-data-interest@imdb.com
- **Commercial Use:** licensing@imdb.com
- **This Project:** Open an issue on GitHub

## 🙏 Acknowledgments

- **IMDB** for providing free non-commercial datasets
- **Flask** community for excellent documentation
- **Render** for free hosting
- All contributors and users!

## 📜 Project History

This web application is converted from a desktop GUI application (`imdb_gui_gpt.py`). The desktop version includes additional features like:
- Genre button visual states
- Director filmography popups
- Logarithmic vote sliders
- Right-click context menus

Both versions share the same database and filtering logic.

---

**⭐ If you find this useful, please star the repository!**

Made with ❤️ and Python
