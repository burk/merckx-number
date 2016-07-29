#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>

using namespace std;

void floyd(vector<vector<int> >& dist, vector<vector<int> >& next) {
	int n = dist.size();

	for (int k = 0; k < n; ++k) {
		for (int i = 0; i < n; ++i) {
			for (int j = 0; j < n; ++j) {
				if (dist[i][k] + dist[k][j] < dist[i][j]) {
					dist[i][j] = dist[i][k] + dist[k][j];
					next[i][j] = next[i][k];
				}
			}
		}
	}
}

int main(int argc, char *argv[]) {
	int n;

	cin >> n;

	vector<vector<int> > dist(n, vector<int>(n));
	vector<vector<int> > next(n, vector<int>(n, -1));

	for (int i = 0; i < n; ++i) {
		for (int j = 0; j < n; ++j) {
			cin >> dist[i][j];
			if (dist[i][j] < 1000000)
				next[i][j] = j;
		}
	}

	floyd(dist, next);

	ofstream ffdist("dist");
	for (int i = 0; i < n; ++i) {
		for (int j = 0; j < n; ++j) {
			ffdist << dist[i][j] << " ";
		}
		ffdist << endl;
	}
	ofstream ffnext("next");
	for (int i = 0; i < n; ++i) {
		for (int j = 0; j < n; ++j) {
			ffnext << next[i][j] << " ";
		}
		ffnext << endl;
	}
	ffdist.close();
	ffnext.close();
}

