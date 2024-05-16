import psb2


def generate_psb2(prob_name: str, data_size: int, seed: int) -> None:
    train_data, test_data = psb2.fetch_examples('psb2-bench/tempfolder/', prob_name, data_size, data_size, format='lists', seed=seed)
    print(train_data[:4])
    print(test_data[:4])
    
    inval = []
    outval = []
    for i, o in train_data:
        inval.append(i)
        if prob_name not in ('coin-sums', 'cut-vector', 'find-pair', 'mastermind'):
            outval.append(o)
        else:
            outval.append([tuple(o)])

    with open('psb2-bench/' + prob_name + '/' + 'Train.txt', 'w') as f:
        f.write(f'inval = {str(inval)}\noutval = {str(outval)}')

    inval = []
    outval = []
    for i, o in test_data:
        inval.append(i)
        if prob_name not in ('coin-sums', 'cut-vector', 'find-pair', 'mastermind'):
            outval.append(o)
        else:
            outval.append([tuple(o)])

    with open('psb2-bench/' + prob_name + '/' + 'Test.txt', 'w') as f:
        f.write(f'inval = {str(inval)}\noutval = {str(outval)}')


if __name__ == '__main__':
    for prob_name in psb2.PROBLEMS:
        generate_psb2(prob_name, 1000, 42)
